/*
**  Copyright (C) Optumi Inc - All rights reserved.
**
**  You may only use this code under license with Optumi Inc and any distribution or modification is strictly prohibited.
**  To receive a copy of the licensing terms please write to contact@optumi.com or visit us at http://www.optumi.com.
**/

import { Global } from '../Global';

import { ServerConnection } from '@jupyterlab/services';
import { ISignal, Signal } from '@lumino/signaling';

import FileServerUtils from '../utils/FileServerUtils';
import { FileMetadata } from '../components/deploy/fileBrowser/FileBrowser';
import { Snackbar } from './Snackbar';

enum UploadStatus {
    COMPLETED = -1,
    STORAGE_LIMIT = -2,
    UPLOAD_SIZE = -3
}

class FileProgress {
    public path: string
    public key: string
    public type: 'upload' | 'download' | 'compression'
    private _progress: number
    public total: number
    // We will keep track to progress that hasn't budged and ignore it after a while
    private sameProgressCounter: number

    constructor(path: string, key: string, type: 'upload' | 'download' | 'compression') {
        this.path = path;
        this.key = key;
        this.type = type;
        this._progress = 0;
        this.total = -1;
    }

    public get progress(): number {
        return this._progress;
    }

    // We will keep track of non-changing progress so we can eventually treat it as done
    // This is too add resiliency to the extension in case the sever does something wrong
    public set progress(progress: number) {
        if (this._progress == progress) {
            // If this is done uploading, we don't want to forget it early
            if (this._progress < this.total) this.sameProgressCounter++;
        } else {
            this.sameProgressCounter = 0;
            this._progress = progress;
        }
    }

    // We expect the progress number to be set to -1 when it is done
    // This is to avoid timing holes where the extension thinks files are uploaded but the controller is still in the process of uploading them to blob storage
    public isDone = (): boolean => {
        return this.progress < 0 || this.sameProgressCounter > 20;
    }

    // Cancel this progress
    public cancel = async () => {
		const settings = ServerConnection.makeSettings();
		const url = settings.baseUrl + "optumi/cancel-progress";
		const init: RequestInit = {
			method: 'POST',
			body: JSON.stringify({
                key: this.path + this.key,
			}),
		};
		ServerConnection.makeRequest(
			url,
			init, 
			settings
		).then((response: Response) => {
			Global.handleResponse(response);
		});
	}
}

export class FileTracker {
	private polling = false;
    private fileProgress: FileProgress[]
    private _files: FileMetadata[]
    public total: number = 0
    public limit: number = 0

	constructor() {
		this.polling = true;
        this.fileProgress = [];
        // We use an empty request to get all progress that the server knows about
        this.receiveCompressionUpdates(true);
        this.receiveUploadUpdates(true);
        this.receiveDownloadUpdates(true);
        this.receiveUpdate();
	}

    public get = (name: string): FileProgress[] => {
        return [...this.fileProgress.filter(x => x.path == name)]
    }

    public forget = (progress: FileProgress) => {
        this.fileProgress = this.fileProgress.filter(x => x != progress);
    }

    private get compressions() {
        return this.fileProgress.filter(x => x.type == 'compression')
    }

    private get uploads() {
        return this.fileProgress.filter(x => x.type == 'upload')
    }

    private get downloads() {
        return this.fileProgress.filter(x => x.type == 'download')
    }

    public uploadFiles = async (metadata: FileMetadata) => {
        // If there is an unsigned agreement, do not poll
        if (Global.user != null && Global.user.unsignedAgreement) {
            return;
        }

        // If we are already uploading this file, ignore the request
        if (this.compressions.filter(x => x.path == metadata.path).length > 0 || this.uploads.filter(x => x.path == metadata.path).length > 0) return;

        const paths = [];
        if (metadata.type == 'directory') {
            for (let file of (await FileServerUtils.getRecursiveTree(Global.convertOptumiPathToJupyterPath(metadata.path)))) {
                if (file.size <= Global.MAX_UPLOAD_SIZE) {
                    paths.push(Global.convertJupyterPathToOptumiPath(file.path));
                }
            }
        } else {
            paths.push(metadata.path);
        }

        // Make this unique by adding a timestamp
        const key = new Date().toISOString();

		const settings = ServerConnection.makeSettings();
		const url = settings.baseUrl + "optumi/upload-files";
		const init: RequestInit = {
			method: 'POST',
			body: JSON.stringify({
                key: metadata.path + key,
				paths: paths,
                compress: Global.user.compressFilesEnabled,
                storageTotal: this.total,
                storageLimit: this.limit,
                autoAddOnsEnabled: Global.user.autoAddOnsEnabled,
			}),
		};
        if (Global.user.compressFilesEnabled) this.fileProgress.push(new FileProgress(metadata.path, key, 'compression'));
        this.fileProgress.push(new FileProgress(metadata.path, key, 'upload'));
        this._filesChanged.emit(void 0);
        return ServerConnection.makeRequest(
			url,
			init, 
			settings
		).then((response: Response) => {
			Global.handleResponse(response);
		});
	}

    public getNotebookOutputFiles = async (name: string, files: FileMetadata[], workloadUUID: string, moduleUUID: string, overwrite: boolean, savePaths: string[] = []) => {
        // If there is an unsigned agreement, do not poll
        if (Global.user != null && Global.user.unsignedAgreement) {
            return;
        }

        const addPaths = savePaths.length == 0;

        const paths = [];
        const sizes = [];
        for (var file of files) {
            paths.push(file.path);
            if (addPaths) savePaths.push(file.path);
            sizes.push(file.size);
        }
        
        // Make this unique by adding a timestamp
        const key = new Date().toISOString();

		const settings = ServerConnection.makeSettings();
		const url = settings.baseUrl + "optumi/get-notebook-output-files";
		const init: RequestInit = {
			method: 'POST',
			body: JSON.stringify({
				workloadUUID: workloadUUID,
				moduleUUID: moduleUUID,
				key: name + key,
                paths: paths,
                savePaths: savePaths,
                sizes: sizes,
                overwrite: overwrite,
			}),
		};
        this.fileProgress.push(new FileProgress(name, key, 'download'));
        this._filesChanged.emit(void 0);
        return ServerConnection.makeRequest(
			url,
			init, 
			settings
		).then((response: Response) => {
			Global.handleResponse(response);
		});
	}

    public downloadFiles = async (name: string, files: FileMetadata[], overwrite: boolean, savePaths: string[] = [], directory: string = null) => {
        var shortestPath = files[0].path;
        for (let file of files) {
            var newShortest = '';
            for (let i = 0; i < Math.min(shortestPath.length, file.path.length); i++) {
                if (file.path[i] != shortestPath[i]) break;
                newShortest += shortestPath[i];
            }
            shortestPath = newShortest;
        }
        if (Global.shouldLogOnEmit) console.log('SignalEmit (' + new Date().getSeconds() + ')');
        if (files.length == 1) {
            Global.snackbarEnqueue.emit(new Snackbar(
                "Downloading " + shortestPath,
                { variant: 'success', }
            ));
        } else {
            while (!shortestPath.endsWith('/')) {
                shortestPath = shortestPath.substring(0, shortestPath.length-1)
            }
            Global.snackbarEnqueue.emit(new Snackbar(
                "Downloading " + files.length + ' files to ' + shortestPath,
                { variant: 'success', }
            ));
        }

        const addPaths = savePaths.length == 0;

        const paths = [];
        const sizes = [];
        const hashes = [];
        for (var file of files) {
            if (this.fileExists(file)) {
                paths.push(file.path);
                if (addPaths) savePaths.push(file.path);
                sizes.push(file.size);
                hashes.push(file.hash || "");
            }
        }
        
        // Make this unique by adding a timestamp
        const key = new Date().toISOString();

		const settings = ServerConnection.makeSettings();
		const url = settings.baseUrl + "optumi/download-files";
		const init: RequestInit = {
			method: 'POST',
			body: JSON.stringify({
				key: name + key,
                paths: paths,
                savePaths: savePaths,
                sizes: sizes,
                hashes: hashes,
                overwrite: overwrite,
                directory: directory,
			}),
		};
        this.fileProgress.push(new FileProgress(name, key, 'download'));
        this._filesChanged.emit(void 0);
        return ServerConnection.makeRequest(
			url,
			init, 
			settings
		).then((response: Response) => {
			Global.handleResponse(response);
		});
	}

    private compressionPollDelay = 500;
    private receiveCompressionUpdates = async (empty: boolean = false) => {
        if (!this.polling) return;
        // If there is an unsigned agreement, do not poll
        if (Global.user != null && Global.user.unsignedAgreement) {
            setTimeout(() => this.receiveCompressionUpdates(), this.compressionPollDelay);
            return;
        }

        const fileNames: string[] = [];
        for (var compression of this.compressions) {
            if (!compression.isDone()) fileNames.push(compression.path + compression.key);
        }
        if (fileNames.length > 0 || empty) {
            const settings = ServerConnection.makeSettings();
            const url = settings.baseUrl + "optumi/get-compression-progress";
            const init: RequestInit = {
                method: 'POST',
                body: JSON.stringify({
                    keys: fileNames,
                }),
            };
            ServerConnection.makeRequest(
                url,
                init, 
                settings
            ).then((response: Response) => {
                Global.handleResponse(response, true);
                setTimeout(() => this.receiveCompressionUpdates(), this.compressionPollDelay);
                if (response.status == 204) {
                    return;
                }
                return response.json();
            }).then((body: any) => {
                if (body) {
                    var changed = false;
                    for (var merged in body) {
                        const path = merged.slice(0, merged.length - 24)
                        const key = merged.slice(merged.length - 24)
                        const progresses = this.compressions.filter(x => x.path == path && x.key == key);
                        var progress;
                        if (progresses.length == 0) {
                            progress = new FileProgress(path, key, 'compression')
                            this.fileProgress.push(progress);
                            // If we are in the process of compressing, we also want to track the upload that will happen after
                            this.fileProgress.push(new FileProgress(path, key, 'upload'));
                        } else {
                            progress = progresses[0];
                        }
                        progress.progress = body[merged].progress;
                        progress.total = body[merged].total;
                        if (progress.progress < -1) {
                            // This means we failed, so set the file to disabled
                            const metadata = Global.metadata.getMetadata();
                            for (let file of metadata.config.upload.files) {
                                if (file.path == path) {
                                    file.enabled = false;
                                    if (progress.progress == UploadStatus.STORAGE_LIMIT) {
                                        if (Global.shouldLogOnEmit) console.log('SignalEmit (' + new Date().getSeconds() + ')');
                                        Global.snackbarEnqueue.emit(new Snackbar(
                                            "Skipping upload of " + path + ", not enough storage capacity",
                                            { variant: 'warning', }
                                        ));
                                    } else if (progress.progress == UploadStatus.UPLOAD_SIZE) {
                                        if (Global.shouldLogOnEmit) console.log('SignalEmit (' + new Date().getSeconds() + ')');
                                        Global.snackbarEnqueue.emit(new Snackbar(
                                            "Skipping upload of " + path + ", exceeds the maximum size",
                                            { variant: 'warning', }
                                        ));
                                    } else {
                                        console.error("Unhandled file error case " + progress.progress)
                                    }
                                }
                            } 
                            Global.metadata.setMetadata(metadata)
                            
                            changed = true;
                        }
                        if (progress.isDone()) this.forget(progress);
                        changed = true;
                    }
                    if (changed) this._filesChanged.emit(void 0);
                }
            }, (error: ServerConnection.ResponseError) => {
                setTimeout(() => this.receiveCompressionUpdates(), this.compressionPollDelay);
            });
        } else {
            setTimeout(() => this.receiveCompressionUpdates(), this.compressionPollDelay);
        }
	}

    private uploadPollDelay = 500;
    private receiveUploadUpdates = async (empty: boolean = false) => {
        if (!this.polling) return;
        // If there is an unsigned agreement, do not poll
        if (Global.user != null && Global.user.unsignedAgreement) {
            setTimeout(() => this.receiveUploadUpdates(), this.uploadPollDelay);
            return;
        }

        const fileNames: string[] = [];
        for (var upload of this.uploads) {
            if (!upload.isDone()) fileNames.push(upload.path + upload.key);
        }
        if (fileNames.length > 0 || empty) {
            const settings = ServerConnection.makeSettings();
            const url = settings.baseUrl + "optumi/get-upload-progress";
            const init: RequestInit = {
                method: 'POST',
                body: JSON.stringify({
                    keys: fileNames,
                }),
            };
            ServerConnection.makeRequest(
                url,
                init, 
                settings
            ).then((response: Response) => {
                Global.handleResponse(response, true);
                setTimeout(() => this.receiveUploadUpdates(), this.uploadPollDelay);
                if (response.status == 204) {
                    return;
                }
                return response.json();
            }).then((body: any) => {
                if (body) {
                    var changed = false;
                    for (var merged in body) {
                        const path = merged.slice(0, merged.length - 24)
                        const key = merged.slice(merged.length - 24)
                        const progresses = this.uploads.filter(x => x.path == path && x.key == key);
                        var progress;
                        if (progresses.length == 0) {
                            progress = new FileProgress(path, key, 'upload')
                            this.fileProgress.push(progress);
                        } else {
                            progress = progresses[0];
                        }
                        progress.progress = body[merged].progress;
                        progress.total = body[merged].total;
                        if (progress.isDone()) this.forget(progress);
                        changed = true;
                    }
                    if (changed) this._filesChanged.emit(void 0);
                }
            }, (error: ServerConnection.ResponseError) => {
                setTimeout(() => this.receiveUploadUpdates(), this.uploadPollDelay);
            });
        } else {
            setTimeout(() => this.receiveUploadUpdates(), this.uploadPollDelay);
        }
	}

    private downloadPollDelay = 500;
    private receiveDownloadUpdates = async (empty: boolean = false) => {
        if (!this.polling) return;
        // If there is an unsigned agreement, do not poll
        if (Global.user != null && Global.user.unsignedAgreement) {
            setTimeout(() => this.receiveDownloadUpdates(), this.downloadPollDelay);
            return;
        }

        const fileNames: string[] = [];
        for (var download of this.downloads) {
            if (!download.isDone()) fileNames.push(download.path + download.key);
        }
        if (fileNames.length > 0 || empty) {
            const settings = ServerConnection.makeSettings();
            const url = settings.baseUrl + "optumi/get-download-progress";
            const init: RequestInit = {
                method: 'POST',
                body: JSON.stringify({
                    keys: fileNames,
                }),
            };
            ServerConnection.makeRequest(
                url,
                init, 
                settings
            ).then((response: Response) => {
                Global.handleResponse(response, true);
                setTimeout(() => this.receiveDownloadUpdates(), this.downloadPollDelay);
                if (response.status == 204) {
                    return;
                }
                return response.json();
            }).then((body: any) => {
                if (body) {
                    var changed = false;
                    for (var merged in body) {
                        const path = merged.slice(0, merged.length - 24)
                        const key = merged.slice(merged.length - 24)
                        const progresses = this.downloads.filter(x => x.path == path && x.key == key);
                        var progress;
                        if (progresses.length == 0) {
                            progress = new FileProgress(path, key, 'download')
                            this.fileProgress.push(progress);
                        } else {
                            progress = progresses[0];
                        }
                        progress.progress = body[merged].progress;
                        progress.total = body[merged].total;
                        if (progress.isDone()) this.forget(progress);
                        changed = true;
                    }
                    if (changed) this._filesChanged.emit(void 0);
                }
            }, (error: ServerConnection.ResponseError) => {
                setTimeout(() => this.receiveDownloadUpdates(), this.downloadPollDelay);
            });
        } else {
            setTimeout(() => this.receiveDownloadUpdates(), this.downloadPollDelay);
        }
	}

    public deleteFiles = async (files: FileMetadata[]) => {
        // If there is an unsigned agreement, do not poll
        if (Global.user != null && Global.user.unsignedAgreement) {
            return;
        }

        if (Global.shouldLogOnEmit) console.log('SignalEmit (' + new Date().getSeconds() + ')');
        Global.snackbarEnqueue.emit(new Snackbar(
            "Deleting " + (files.length == 1 ? files[0].name : files.length + ' files'),
            { variant: 'success', }
        ));

        this._files.filter(file => !files.map(x => x.hash + x.path).includes(file.hash + file.path));
        this._filesChanged.emit();

        const hashes = []
        const paths = [];
        const creationTimes = [];
        for (var metadata of files) {
            hashes.push(metadata.hash);
            paths.push(metadata.path);
            creationTimes.push(metadata.created);
        }

		const settings = ServerConnection.makeSettings();
		const url = settings.baseUrl + "optumi/delete-files";
		const init: RequestInit = {
			method: 'POST',
			body: JSON.stringify({
				hashes: hashes,
                paths: paths,
                creationTimes: creationTimes,
			}),
		};
        return ServerConnection.makeRequest(
			url,
			init, 
			settings
		).then((response: Response) => {
			Global.handleResponse(response);
            return response.text();
		}).then(() => {
            // The delete request could have resulted in a file being disabled, 
            Global.metadata.refreshMetadata()
            this.receiveUpdate(false);
        });
	}

    private filesPollDelay = 30000;
    private receiveUpdate = async (poll: boolean = true) => {
        if (!this.polling) return;
        // If there is an unsigned agreement, do not poll
        if (Global.user == null || Global.user.unsignedAgreement) {
            setTimeout(() => this.receiveUpdate(), 2000);
            return;
        }

		const settings = ServerConnection.makeSettings();
        const url = settings.baseUrl + "optumi/list-files";
		const init: RequestInit = {
			method: 'GET',
		};
		ServerConnection.makeRequest(
			url,
			init, 
			settings
		).then((response: Response) => {
            Global.handleResponse(response);
			if (poll && this.polling) {
				// If we are polling, send a new request in 30 seconds
                if (Global.shouldLogOnPoll) console.log('FunctionPoll (' + new Date().getSeconds() + ')');
				setTimeout(() => this.receiveUpdate(), this.filesPollDelay);
			}
			return response.json();
		}).then((body: any) => {
			if (body) {
                let newFiles: FileMetadata[] = []
                if (body.total) this.total = +body.total;
                if (body.limit) this.limit = +body.limit;                

                if (body.files) {
                    for (let i = 0; i < body.files.length; i++) {
                        if (body.files[i] != '') {
                            newFiles.push({
                                created: body.filescrt[i],
                                last_modified: body.filesmod[i],
                                name: (body.files[i] as string).split('/').pop(),
                                path: body.files[i],
                                size: +body.filessize[i],
                                type: 'file',
                                hash: body.hashes[i],
                            } as FileMetadata);
                        }
                    }
                }
                // const filesToApps = new Map();
                // const appsToFiles = new Map();
                // const appTracker = Global.user.appTracker;
        
                // // Figure out which apps are associated with which files
                // for (let metadata of newFiles) {
                //     const apps = [];
                //     APP_LOOP:
                //     for (let app of [...appTracker.activeJobsOrSessions, ...appTracker.finishedJobsOrSessions]) {
                //         for (let file of app.files) {
                //             if (file.path === metadata.path) {
                //                 apps.push(app.uuid);
                //                 continue APP_LOOP;
                //             }
                //         }
                //         for (let module of app.modules) {
                //             for (let file of module.files) {
                //                 if (file.path === metadata.path) {
                //                     apps.push(app.uuid);
                //                     continue APP_LOOP;
                //                 }
                //             }
                //         }
                //     }
                //     filesToApps.set(metadata, apps);
                // }

                // // Figure out which files are associated with which apps
                // for (let app of [...appTracker.activeJobsOrSessions, ...appTracker.finishedJobsOrSessions]) {
                //     const files = []
                //     for (let file of app.files) {
                //         files.push(file)
                //     }
                //     for (let module of app.modules) {
                //         for (let file of module.files) {
                //             files.push(file);
                //         }
                //     }
                //     appsToFiles.set(app.uuid, files);
                // }

                this._files = newFiles;
                this._filesChanged.emit();
			}
        }, (error: ServerConnection.ResponseError) => {
            if (poll && this.polling) {
				// If we are polling, send a new request in 30 seconds
                if (Global.shouldLogOnPoll) console.log('FunctionPoll (' + new Date().getSeconds() + ')');
				setTimeout(() => this.receiveUpdate(), this.filesPollDelay);
			}
        });
    }

    public get files(): FileMetadata[] {
        return this._files;
    }

    public fileExists = (metadata: FileMetadata): boolean => {
        if (this._files) {
            const match = metadata.hash + metadata.path;
            for (let file of this._files) {
                if (file.hash + file.path === match) return true;
            }
        }
        return false;
    }

    public pathExists = (path: string): boolean => {
        if (this._files) {
            for (let file of this._files) {
                if (file.path === path) return true;
            }
        }
        return false;
    }

    public directoryExists = (path: string): boolean => {
        if (this._files) {
            for (let file of this._files) {
                if (file.path.startsWith(path)) return true;
            }
        }
        return false;
    }

    public stopPolling = () => {
        this.polling = false;
    }

    public getFilesChanged = (): ISignal<this, void> => {
		return this._filesChanged;
	}

    private _filesChanged = new Signal<this, void>(this);
}
