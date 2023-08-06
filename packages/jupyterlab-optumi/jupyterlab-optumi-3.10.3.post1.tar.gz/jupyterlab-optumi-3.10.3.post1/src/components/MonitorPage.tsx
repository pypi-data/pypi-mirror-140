/*
**  Copyright (C) Optumi Inc - All rights reserved.
**
**  You may only use this code under license with Optumi Inc and any distribution or modification is strictly prohibited.
**  To receive a copy of the licensing terms please write to contact@optumi.com or visit us at http://www.optumi.com.
**/

import * as React from 'react';
import { DIV, Global } from '../Global';

import { SxProps, Theme } from '@mui/system';

import { App } from '../models/application/App';
import { Header, SubHeader } from '../core';

interface IProps {
	sx?: SxProps<Theme>
	openUserDialogTo?: (page: number) => Promise<void> // This is somewhat spaghetti code-y, maybe think about revising
}

interface IState {}

// Defaults for this component
const DefaultState: IState = {}

export class MonitorPage extends React.Component<IProps, IState> {
	state = DefaultState;

	private generateActive = (apps: App[]) => {
		var sorted: App[] = apps.sort((n1,n2) => {
			if (n1.timestamp > n2.timestamp) {
				return -1;
			}
			if (n1.timestamp < n2.timestamp) {
				return 1;
			}
			return 0;
		});
		return sorted.map(value => (
				<DIV key={value.uuid} sx={{padding: '6px 0px 6px 6px'}}>
					{value.getComponent(this.props.openUserDialogTo)}
				</DIV>
			)
		);
	}

	private generateFinished = (apps: App[]) => {
		var sorted: App[] = apps.sort((n1,n2) => {
			if ((n1.getEndTime() || n1.timestamp) > (n2.getEndTime() ||  n2.timestamp)) {
				return -1;
			}
			if ((n1.getEndTime() || n1.timestamp) < (n2.getEndTime() ||  n2.timestamp)) {
				return 1;
			}
			return 0;
		});
		return sorted.map(value => (
				<DIV key={value.uuid} sx={{padding: '6px 0px 6px 6px'}}>
					{value.getComponent(this.props.openUserDialogTo)}
				</DIV>
			)
		);
	}

	// The contents of the component
	public render = (): JSX.Element => {
		if (Global.shouldLogOnRender) console.log('ComponentRender (' + new Date().getSeconds() + ')');
		const appTracker = Global.user.appTracker;
		return (
			<DIV sx={Object.assign({overflowY: 'auto'}, this.props.sx)}>
				<DIV sx={{padding: '6px'}}>
					<Header title="Active" />
					{appTracker.activeSessions.length != 0 ? (
						<>
							<SubHeader title="Sessions" />
							{this.generateActive(appTracker.activeSessions)}
						</>
					) : (
						<DIV sx={{display: 'inline-flex', width: '100%'}}>
							<SubHeader title="Sessions" grey />
							<DIV sx={{ 
									margin: '6px 0px',
									fontSize: '14px',
									lineHeight: '18px',
									opacity: 0.5
								}}>
								(none)
							</DIV>
						</DIV>
					)}
					{appTracker.activeJobs.length != 0 ? (
						<>
							<SubHeader title="Jobs" grey />
							{this.generateActive(appTracker.activeJobs)}
						</>
					) : (
						<DIV sx={{display: 'inline-flex', width: '100%'}}>
							<SubHeader title="Jobs" grey />
							<DIV sx={{ 
								margin: '6px 0px',
								fontSize: '14px',
								lineHeight: '18px',
								opacity: 0.5
							}}>
								(none)
							</DIV>
						</DIV>
					)}
				</DIV>
				<DIV sx={{padding: '6px'}}>
					<Header title="Finished" />
					{appTracker.finishedSessions.length != 0 ? (
						<>
							<SubHeader title="Sessions" grey />
							{this.generateFinished(appTracker.finishedSessions)}
						</>
					) : (
						<DIV sx={{display: 'inline-flex', width: '100%'}}>
							<SubHeader title="Sessions" grey />
							<DIV sx={{ 
								margin: '6px 0px',
								fontSize: '14px',
								lineHeight: '18px',
								opacity: 0.5
							}}>
								(none)
							</DIV>
						</DIV>
					)}
					{appTracker.finishedJobs.length != 0 ? (
						<>
							<SubHeader title="Jobs" grey />
							{this.generateFinished(appTracker.finishedJobs)}
						</>
					) : (
						<DIV sx={{display: 'inline-flex', width: '100%'}}>
							<SubHeader title="Jobs" grey />
							<DIV sx={{ 
								margin: '6px 0px',
								fontSize: '14px',
								lineHeight: '18px',
								opacity: 0.5
							}}>
								(none)
							</DIV>
						</DIV>
					)}
				</DIV>
			</DIV>
		);
	}

	private handleAppChange = () => { this.forceUpdate() }

	// Will be called automatically when the component is mounted
	public componentDidMount = () => {
		Global.user.appTracker.appsChanged.connect(this.handleAppChange);
	}

	// Will be called automatically when the component is unmounted
	public componentWillUnmount = () => {
		Global.user.appTracker.appsChanged.disconnect(this.handleAppChange);
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
}
