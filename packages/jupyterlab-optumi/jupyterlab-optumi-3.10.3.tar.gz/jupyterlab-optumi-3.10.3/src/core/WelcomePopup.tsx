/*
**  Copyright (C) Optumi Inc - All rights reserved.
**
**  You may only use this code under license with Optumi Inc and any distribution or modification is strictly prohibited.
**  To receive a copy of the licensing terms please write to contact@optumi.com or visit us at http://www.optumi.com.
**/

import { ServerConnection } from '@jupyterlab/services';


import * as React from 'react'
import { DIV, Global, LI, UL } from '../Global';

import {
    Button,
    CircularProgress,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Theme,
} from '@mui/material';
import { withStyles } from '@mui/styles';

import { ShadowedDivider } from './ShadowedDivider'
import { PlansPopup } from './PlansPopup';
import { User } from '../models/User';

const StyledDialog = withStyles((theme: Theme) => ({
    root: {
        margin: '12px',
        padding: '0px',
    },
    paper: {
        backgroundColor: 'var(--jp-layout-color1)',
    },
}))(Dialog)

interface IProps {}

interface IState {
    plansOpen: boolean
    freeTrialWaiting: boolean
}

export default class WelcomePopup extends React.Component<IProps, IState> {
    private _isMounted = false

    public constructor(props: IProps) {
        super (props);
        this.state = {
            plansOpen: false,
            freeTrialWaiting: false
        }
    }

    // Log out of the REST interface (Copied from SettingsPage aside from setState call)
    private logout = () => {
        const settings = ServerConnection.makeSettings();
        const url = settings.baseUrl + "optumi/logout";
        const init = {
            method: 'GET',
        };
        ServerConnection.makeRequest(
            url,
            init, 
            settings
        ).then((response: Response) => {
            Global.user = null;
            this.safeSetState({open: false})
        });
    }

    public render = (): JSX.Element => {
		if (Global.shouldLogOnRender) console.log('ComponentRender (' + new Date().getSeconds() + ')');
        return (
            <StyledDialog
                onClose={(event: object, reason: string) => void 0}
                open={Global.user.trialStart == null && !Global.user.subscriptionActive}
            >
                <DialogTitle sx={{
                        display: 'inline-flex',
                        height: '60px',
                        padding: '6px',
                    }}>
                        <DIV sx={{
                            display: 'inline-flex',
                            minWidth: '150px',
                            fontSize: '16px',
                            fontWeight: 'bold',
                            paddingRight: '12px', // this is 6px counteracting the DialogTitle padding and 6px aligning the padding to the right of the tabs
                        }}>
                            <DIV sx={{margin: 'auto', paddingLeft: '12px'}}>
                                Welcome 👋
                            </DIV>
                        </DIV>
                        <DIV sx={{flexGrow: 1}} />
                        <DIV>
                            <Button
                                disableElevation
                                sx={{ height: '36px', margin: '6px' }}
                                variant="outlined"
                                color="primary"
                                onClick={() => {
                                    const user: User = Global.user;
                                    if (user.appTracker.activeSessions.length != 0) {
                                        this.safeSetState({ showLogoutWithSessionPopup: true });
                                    } else {
                                        this.logout()
                                    }
                                }}
                            >
                                Logout
                            </Button>
                        </DIV>
					</DialogTitle>
                <ShadowedDivider />
                <DIV sx={{padding: '18px'}}>
                    <DialogContent sx={{padding: '6px 18px', whiteSpace: 'pre-wrap'}}>
                        A few things to remember about your free trial:
                        <UL>
                            <LI>No credit card required</LI>
                            <LI>It is valid for 2 weeks</LI>
                            <LI>You get a $5 promotional credit for machines to run notebooks</LI>
                            <LI>At the end of the trial your promotional credit will expire and your data will be deleted (unless you subscribe!)</LI>
                        </UL>
                    </DialogContent>
                    <DialogActions sx={{padding: '12px 6px 6px 6px'}}>
                        <PlansPopup
                            open={this.state.plansOpen}
                            handleClose={() => this.safeSetState({ plansOpen: false })}
                            openButton={
                                <Button
                                    sx={{margin: '12px'}}
                                    variant='outlined'
                                    color='primary'
                                    onClick={() => this.safeSetState({ plansOpen: true })}
                                >
                                    View plans
                                </Button>
                            }
                            buttons={
                                <>
                                    <Button
                                        sx={{margin: '12px', width: '160px'}}
                                        variant='outlined'
                                        color='primary'
                                        onClick={() => this.safeSetState({ plansOpen: false })}
                                    >
                                        Start with free trial
                                    </Button>
                                </>
                            }
                        />
                        <Button
                            variant='contained'
                            color='primary'
                            onClick={() => {
                                Global.user.trialStart = new Date()
                                this.safeSetState({freeTrialWaiting: true})
                            }}
                            sx={{marginLeft: '18x'}}
                        >
                            {this.state.freeTrialWaiting ? (<CircularProgress size='1.75em'/>) : 'Start free trial'}
                        </Button>
                    </DialogActions>
                </DIV>
           </StyledDialog>
        );
    }

    public componentDidMount = () => {
        this._isMounted = true
    }

    public componentWillUnmount = () => {
        this._isMounted = false
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
}
