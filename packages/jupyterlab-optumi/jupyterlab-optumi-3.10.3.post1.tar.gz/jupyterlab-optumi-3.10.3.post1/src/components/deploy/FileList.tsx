/*
**  Copyright (C) Optumi Inc - All rights reserved.
**
**  You may only use this code under license with Optumi Inc and any distribution or modification is strictly prohibited.
**  To receive a copy of the licensing terms please write to contact@optumi.com or visit us at http://www.optumi.com.
**/

import * as React from 'react';
import { DIV, Global } from '../../Global';

import { IconButton } from '@mui/material';
import { GetApp as GetAppIcon } from '@mui/icons-material';

import { FileMetadata } from './fileBrowser/FileBrowser';
import { FileTree } from '../FileTree';
import { App } from '../../models/application/App';
import FileServerUtils from '../../utils/FileServerUtils';

import moment from 'moment';
import FormatUtils from '../../utils/FormatUtils';

interface IProps {
	app: App;
}

// Properties for this component
interface IState {
	overwrite: boolean
}

export class FileList extends React.Component<IProps, IState> {
	_isMounted = false;

	constructor(props: IProps) {
		super(props);
		this.state = {
			overwrite: false
		};
	}

	private getFileHidableIcon = (file: FileMetadata) => {
		return {
			width: 36,
			height: 36,
			icon: (
				<IconButton
                    size='large'
					disabled={!Global.user.fileTracker.fileExists(file)}
                    onClick={() => this.downloadFile(file)}
                    sx={{ width: '36px', height: '36px', padding: '3px' }}
                >
					<GetAppIcon sx={{ width: '30px', height: '30px', padding: '3px' }} />
				</IconButton>
			),
		};
	}

	private getFiles() {
		const inputFiles: FileMetadata[] = [];
		const outputFiles: FileMetadata[] = [];
		for (let module of this.props.app.modules) {
            if (module.files) {
                for (let file of module.files) {
                    outputFiles.push(file);
                }
            }
		}
		for (let file of this.props.app.files) {
			inputFiles.push(file);
		}
		var sortedInput: FileMetadata[] = inputFiles.sort(FileServerUtils.sortFiles);
		var sortedOutput: FileMetadata[] = outputFiles.sort(FileServerUtils.sortFiles);
		const log = { name: this.props.app.path.replace('.ipynb', '.log').replace(/^.*\/([^/]*)$/, '$1'), path: '~/' + this.props.app.path.replace('.ipynb', '.log'), size: 0 } as FileMetadata;
		return (
            <DIV>
				<DIV>
					<DIV sx={{fontWeight: 'bold'}}>
						Input files
					</DIV>
					{sortedInput.length == 0 ? (
						<DIV>
							No input files
						</DIV>
					) : (
						<FileTree
							files={sortedInput}
							fileTitle={file => (
`Name: ${file.name}
${file.size === null ? '' : `Size: ${FormatUtils.styleCapacityUnitValue()(file.size)} (${file.size} bytes)
`}${file.path === '' ? '' : `Path: ${file.path.replace(file.name, '').replace(/\/$/, '')}
`}Modified: ${moment(file.last_modified).format('YYYY-MM-DD hh:mm:ss')}`
							)}
							fileHidableIcon={this.getFileHidableIcon}
							directoryHidableIcon={path => ({
								width: 36,
								height: 36,
								icon: (
									<IconButton
                                        size='large'
                                        onClick={() => this.downloadDirectory(path, sortedInput)}
                                        sx={{ width: '36px', height: '36px', padding: '3px' }}
                                    >
										<GetAppIcon sx={{ width: '30px', height: '30px', padding: '3px' }} />
									</IconButton>
								),
							})}
						/>
					)}
				</DIV>
				<DIV>
					<DIV sx={{fontWeight: 'bold', marginTop: '16px'}}>
						Output files
					</DIV>
					{sortedOutput.length == 0 ? (
						<DIV>
							No output files
						</DIV>
					) : (
						<FileTree
							files={[log].concat(sortedOutput)}
							fileTitle={file => (
`Name: ${file.name}
${file.size === null ? '' : `Size: ${FormatUtils.styleCapacityUnitValue()(file.size)} (${file.size} bytes)
`}${file.path === '' ? '' : `Path: ${file.path.replace(file.name, '').replace(/\/$/, '')}
`}Modified: ${moment(file.last_modified).format('YYYY-MM-DD hh:mm:ss')}`
							)}
							fileHidableIcon={this.getFileHidableIcon}
							directoryHidableIcon={path => ({
								width: 36,
								height: 36,
								icon: (
									<IconButton
                                        size='large'
                                        onClick={() => this.downloadDirectory(path, [log].concat(sortedOutput))}
                                        sx={{ width: '36px', height: '36px', padding: '3px' }}
                                    >
										<GetAppIcon sx={{ width: '30px', height: '30px', padding: '3px' }} />
									</IconButton>
								),
							})}
						/>
					)}
				</DIV>
			</DIV>
        );
	}

	private downloadFile = (file: FileMetadata) => {
		if (file.hash) {
			Global.user.fileTracker.downloadFiles(file.path, [file], false);
		} else {
			Global.user.fileTracker.getNotebookOutputFiles(file.path, [file], this.props.app.uuid, this.props.app.modules[0].uuid, false);
		}
	}

	private downloadDirectory = (path: string, files: FileMetadata[]) => {
		const withHashes = [];
		const withoutHashes = [];
        for (let file of files) {
            if (file.path.startsWith('~/' + path)) {
                if (file.hash) {
					withHashes.push(file);
				} else {
					withoutHashes.push(file);
				}
            }
        }
		if (withHashes.length > 0) Global.user.fileTracker.downloadFiles(path, withHashes, false, [], path);
		if (withoutHashes.length > 0) Global.user.fileTracker.getNotebookOutputFiles(path, withoutHashes, this.props.app.uuid, this.props.app.modules[0].uuid, false);
	}

	public render = (): JSX.Element => {
		if (Global.shouldLogOnRender) console.log('ComponentRender (' + new Date().getSeconds() + ')');
		return (
			<DIV sx={{padding: '12px', width: "100%"}}>
				{this.getFiles()}
			</DIV>
		);
	}

	// Will be called automatically when the component is mounted
	public componentDidMount = () => {
		this._isMounted = true;
	}

	// Will be called automatically when the component is unmounted
	public componentWillUnmount = () => {
		this._isMounted = false;
	}

	// private safeSetState = (map: any) => {
	// 	if (this._isMounted) {
	// 		let update = false
	// 		try {
	// 			for (const key of Object.keys(map)) {
	// 				if (JSON.stringify(map[key]) !== JSON.stringify((this.state as any)[key])) {
	// 					update = true
	// 					break
	// 				}
	// 			}
	// 		} catch (error) {
	// 			update = true
	// 		}
	// 		if (update) {
	// 			if (Global.shouldLogOnSafeSetState) console.log('SafeSetState (' + new Date().getSeconds() + ')');
	// 			this.setState(map)
	// 		} else {
	// 			if (Global.shouldLogOnSafeSetState) console.log('SuppressedSetState (' + new Date().getSeconds() + ')');
	// 		}
	// 	}
	// }

	public shouldComponentUpdate = (nextProps: IProps, nextState: IState): boolean => {
        try {
            if (JSON.stringify(this.props) != JSON.stringify(nextProps)) return true;
            if (JSON.stringify(this.state) != JSON.stringify(nextState)) return true;
            if (Global.shouldLogOnRender) console.log('SuppressedRender (' + new Date().getSeconds() + ')');
            return false;
        } catch (error) {
            return true;
        }
    }
}
