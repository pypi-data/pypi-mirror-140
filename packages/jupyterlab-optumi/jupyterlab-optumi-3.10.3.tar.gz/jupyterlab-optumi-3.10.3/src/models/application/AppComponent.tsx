/*
**  Copyright (C) Optumi Inc - All rights reserved.
**
**  You may only use this code under license with Optumi Inc and any distribution or modification is strictly prohibited.
**  To receive a copy of the licensing terms please write to contact@optumi.com or visit us at http://www.optumi.com.
**/

import * as React from 'react';
import { Global } from '../../Global';

import { IconButton, CircularProgress } from '@mui/material';
import { Clear as ClearIcon, Check as CheckIcon, Delete as DeleteIcon, Stop as StopIcon } from '@mui/icons-material';

import { ServerConnection } from '@jupyterlab/services';

import { Status } from '../Module';
import { InfoSkirt } from '../../components/InfoSkirt';
import { StatusWrapper } from '../../components/StatusWrapper';
import { Tag } from '../../components/Tag';
import WarningPopup from '../../core/WarningPopup';
import ExtraInfo from '../../utils/ExtraInfo';
import { App } from './App';
import { Colors } from '../../Colors';

interface IProps {
	app: App,
	openUserDialogTo?: (page: number) => Promise<void> // This is somewhat spaghetti code-y, maybe think about revising
}

interface IState {
	opened: boolean;
	waiting: boolean;
	spinning: boolean;
	showDeleteJobPopup: boolean;
	showStopJobPopup: boolean;
}

export class AppComponent extends React.Component<IProps, IState> {
	_isMounted = false;

    constructor(props: IProps) {
        super(props);
        this.state = {
			opened: false,
			waiting: false,
			spinning: false,
			showDeleteJobPopup: false,
			showStopJobPopup: false,
        };
    }

	private getDeleteJobPreventValue = (): boolean => {
		return Global.user.deleteJobPreventEnabled;
	}

	private saveDeleteJobPreventValue = (prevent: boolean) => {
		Global.user.deleteJobPreventEnabled = prevent;
	}

	private handleDeleteClicked = () => {
		this.safeSetState({ waiting: true, spinning: false });
		setTimeout(() => this.safeSetState({ spinning: true }), 1000);
		const settings = ServerConnection.makeSettings();
		const url = settings.baseUrl + "optumi/teardown-notebook";
		const init: RequestInit = {
			method: 'POST',
			body: JSON.stringify({
				workload: this.props.app.uuid,
			}),
		};
		ServerConnection.makeRequest(
			url,
			init,
			settings
		).then((response: Response) => {
			this.safeSetState({ waiting: false });
			Global.handleResponse(response);
			Global.user.appTracker.removeApp(this.props.app.uuid);
		});
    }
	
	private getStopJobPreventValue = (): boolean => {
		return Global.user.stopJobPreventEnabled;
	}

	private saveStopJobPreventValue = (prevent: boolean) => {
		Global.user.stopJobPreventEnabled = prevent;
	}

    private handleStopClicked = () => {
		this.safeSetState({ waiting: true, spinning: false });
		setTimeout(() => this.safeSetState({ spinning: true }), 1000);
		const settings = ServerConnection.makeSettings();
		const url = settings.baseUrl + "optumi/stop-notebook";
		const init: RequestInit = {
			method: 'POST',
			body: JSON.stringify({
				workload: this.props.app.uuid,
				module: this.props.app.modules[0].uuid,
			}),
		};
		ServerConnection.makeRequest(
			url,
			init,
			settings
		).then((response: Response) => {
			this.safeSetState({ waiting: false })
			Global.handleResponse(response);
		});
	}

	private getStatusColor = (): string => {
		if (this.props.app.getAppMessage() == 'Closed' || this.props.app.getAppMessage() == 'Terminated') {
			return Colors.DISABLED;
		}
		if (this.props.app.getError()) {
			return Colors.ERROR;
		} else {
			const appStatus = this.props.app.getAppStatus();
			if (appStatus == Status.INITIALIZING) {
				return Colors.PRIMARY;
			} else {
				return Colors.SUCCESS;
			}
		}
	}

	public render = (): JSX.Element => {
		if (Global.shouldLogOnRender) console.log('ComponentRender (' + new Date().getSeconds() + ')');
		var tags: JSX.Element[] = []
		var app: App = this.props.app

		// Get the right progress message...
		var appMessage = app.getAppMessage();
		tags.push(
			<ExtraInfo key={'appMessage'} reminder={'Status'}>
				<Tag key={'appMessage'}
					id={app.uuid + appMessage}
					icon={
						app.getAppStatus() == Status.COMPLETED ? (
							app.getAppMessage() == 'Closed' || app.getAppMessage() == 'Terminated' ? (
								<ClearIcon sx={{
									height: '14px',
									width: '14px',
									fill: 'gray',
								}} />
							) : (
							(app.getError() ? (
								<ClearIcon sx={{
									height: '14px',
									width: '14px',
									fill: '#ffffff',
								}} />
							) : (
								<CheckIcon sx={{
									height: '14px',
									width: '14px',
									fill: '#ffffff',
								}} />
							))
						)) : undefined}
					label={appMessage}
					color={(this.props.app.getShowLoading() || app.getAppStatus() == Status.COMPLETED) ? this.getStatusColor() : undefined}
					solid={app.getAppStatus() == Status.COMPLETED && (app.getAppMessage() != 'Closed' && app.getAppMessage() != 'Terminated')}
					showLoading={this.props.app.getShowLoading()}
					percentLoaded={undefined}
				/>
			</ExtraInfo>
		)
        var appElapsed = app.getTimeElapsed();
		tags.push(
			<ExtraInfo key={'appElapsed'} reminder='Duration'>
				<Tag key={'appElapsed'} label={appElapsed} />
			</ExtraInfo>
		)
		var appCost = app.getCost();
		if (appCost) {
			tags.push(
				<ExtraInfo key={'appCost'} reminder='Approximate machine cost'>
					<Tag key={'appCost'} label={appCost} />
				</ExtraInfo>
			)
		}
        return <>
            <StatusWrapper key={this.props.app.uuid} statusColor={app.getAppStatus() == Status.COMPLETED ? 'var(--jp-layout-color2)' : this.getStatusColor()} opened={this.state.opened}>
                <InfoSkirt
                    leftButton={
                        <ExtraInfo reminder='See details'>
                            {this.props.app.getPopupComponent(() => this.safeSetState({ opened: true }), () => this.safeSetState({ opened: false }), this.props.openUserDialogTo)}
                        </ExtraInfo>
                    }
                    rightButton={(this.props.app.preparing.completed && !this.props.app.preparing.error) && !this.props.app.running.completed ? (
                        <>
                            <WarningPopup
                                open={this.state.showStopJobPopup}
                                headerText="Are you sure?"
                                bodyText={(() => {
                                    if (this.props.app.interactive) {
                                        return "This session is active. If you close it, the session cannot be resumed."
                                    } else {
                                        return "This job is running. If you terminate it, the job cannot be resumed."
                                    }
                                })()}
                                preventText="Don't ask me again"
                                cancel={{
                                    text: `Cancel`,
                                    onCancel: (prevent: boolean) => {
                                        // this.saveStopJobPreventValue(prevent)
                                        this.safeSetState({ showStopJobPopup: false })
                                    },
                                }}
                                continue={{
                                    text: (() => {
                                        if (this.props.app.interactive) {
                                            return "Close it"
                                        } else {
                                            return "Terminate it"
                                        }
                                    })(),
                                    onContinue: (prevent: boolean) => {
                                        this.safeSetState({ showStopJobPopup: false })
                                        this.saveStopJobPreventValue(prevent)
                                        this.handleStopClicked()
                                    },
                                    color: `error`,
                                }}
                            />
                            <IconButton
                                size='large'
                                disabled={this.state.waiting}
                                onClick={() => {
                                    if (this.getStopJobPreventValue()) {
                                        this.handleStopClicked()
                                    } else {
                                        this.safeSetState({ showStopJobPopup: true })
                                    }
                                }}
                                sx={{
                                    position: 'relative',
                                    display: 'inline-block',
                                    width: '36px',
                                    height: '36px',
                                    padding: '3px',
                                }}
                            >
                                <ExtraInfo reminder={this.props.app.interactive ? 'Stop' : 'Terminate'}>
                                    <StopIcon sx={{
                                        position: 'relative',
                                        width: '30px',
                                        height: '30px',
                                        padding: '3px',
                                    }} />
                                </ExtraInfo>
                                {this.state.waiting && this.state.spinning && <CircularProgress size='30px' sx={{position: 'absolute', left: '3px', top: '3px'}} />}
                            </IconButton>
                        </>
                    ) : (
                        <>
                            <WarningPopup
                                open={this.state.showDeleteJobPopup}
                                headerText="Are you sure?"
                                bodyText={(() => {
                                    if (this.props.app.interactive) {
                                        return "You will lose all session information and any files that have not been downloaded. This cannot be undone."
                                    } else {
                                        return "You will lose all job information and any files that have not been downloaded. This cannot be undone."
                                    }
                                })()}
                                preventText="Don't ask me again"
                                cancel={{
                                    text: `Cancel`,
                                    onCancel: (prevent: boolean) => {
                                        // this.saveDeleteJobPreventValue(prevent)
                                        this.safeSetState({ showDeleteJobPopup: false })
                                    },
                                }}
                                continue={{
                                    text: `Delete it`,
                                    onContinue: (prevent: boolean) => {
                                        this.safeSetState({ showDeleteJobPopup: false })
                                        this.saveDeleteJobPreventValue(prevent)
                                        this.handleDeleteClicked()
                                    },
                                    color: `error`,
                                }}
                            />
                            <ExtraInfo reminder='Delete'>
                                <IconButton
                                    size='large'
                                    disabled={this.state.waiting || !this.props.app.initializing.completed}
                                    onClick={() => {
                                        if (this.getDeleteJobPreventValue() || !this.props.app.running.started) {
                                            this.handleDeleteClicked()
                                        } else {
                                            this.safeSetState({ showDeleteJobPopup: true })
                                        }
                                    }}
                                    sx={{position: 'relative', display: 'inline-block', width: '36px', height: '36px', padding: '3px'}}
                                >
                                    <DeleteIcon sx={{position: 'relative', width: '30px', height: '30px', padding: '3px'}} />
                                    {this.state.waiting && this.state.spinning && <CircularProgress size='30px' sx={{position: 'absolute', left: '3px', top: '3px'}} />}
                                </IconButton>
                            </ExtraInfo>
                        </>
                    )}
                    tags={tags}
                >
                    {this.props.app.getIdentityComponent()}
                </InfoSkirt>
            </StatusWrapper>
        </>;
	}

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

	private safeSetState = (map: any) => {
		if (this._isMounted) {
			let update = false
			try {
				for (const key of Object.keys(map)) {
					if (JSON.stringify(map[key]) !== JSON.stringify((this.state as any)[key])) {
						update = true
						break
					}
				}
			} catch (error) {
				update = true
			}
			if (update) {
				if (Global.shouldLogOnSafeSetState) console.log('SafeSetState (' + new Date().getSeconds() + ')');
				this.setState(map)
			} else {
				if (Global.shouldLogOnSafeSetState) console.log('SuppressedSetState (' + new Date().getSeconds() + ')');
			}
		}
	}

	// Will be called automatically when the component is mounted
	public componentDidMount = () => {
        this._isMounted = true;
	}

	// Will be called automatically when the component is unmounted
	public componentWillUnmount = () => {
		this._isMounted = false;
	}
}
