///<reference path="../../node_modules/@types/node/index.d.ts"/>

/*
**  Copyright (C) Optumi Inc - All rights reserved.
**
**  You may only use this code under license with Optumi Inc and any distribution or modification is strictly prohibited.
**  To receive a copy of the licensing terms please write to contact@optumi.com or visit us at http://www.optumi.com.
**/

import * as React from 'react';
import { DIV, Global, TEXTAREA } from '../Global';

import {
    Container,
    Button,
    CircularProgress,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
} from '@mui/material';
import { withStyles } from '@mui/styles';

import { ServerConnection } from '@jupyterlab/services';

import { User } from '../models/User';
import { Header, ShadowedDivider } from '../core';

const StyledDialog = withStyles({
    root: {
        margin: '12px',
        padding: '0px',
    },
    paper: {
        backgroundColor: 'var(--jp-layout-color1)',
    },
})(Dialog)

// Properties from parent
interface IProps {
	
}

// Properties for this component
interface IState {
	loginFailed: boolean;
	loginFailedMessage: string;
	waiting: boolean;
	packageString: string;
	downgrade: boolean;

	progress: string;
	showLoginHint: boolean;
	showAllocatingHint: boolean;
}

// The login screen
export class OauthLogin extends React.Component<IProps, IState> {
	_isMounted = false;
	private observer: MutationObserver;
	// Avoid rapid login attempts
	private lastLoginAttempt: Date = new Date(0)

	constructor(props: IProps) {
		super(props);
		this.state = {
			loginFailed: false,
            loginFailedMessage: "",
			waiting: false,
			packageString: "",
			downgrade: false,

			progress: undefined,
			showLoginHint: false,
			showAllocatingHint: false,
		}
		this.observer = new MutationObserver((mutations) => {
			mutations.forEach((mutationRecord: any) => {
				if (!(mutationRecord.target.classList as DOMTokenList).contains('lm-mod-hidden')) {
					this.check_login(true);
				}
			});    
		});
	}

	private getMessage = (): string => {
		if (this.state.loginFailedMessage != "") {
			return this.state.loginFailedMessage
		} else {
			return this.state.progress
		}
	}

	// The contents of the component
	public render = (): JSX.Element => {
		if (Global.shouldLogOnRender) console.log('ComponentRender (' + new Date().getSeconds() + ')');
		return <>
            <div className='jp-optumi-logo'/>
            <Container sx={{textAlign: 'center'}} maxWidth="xs">
                {this.state.waiting ? (
                    <CircularProgress size='3em'/>
                ) : (
                    <Button
                        sx={{margin: '16px', minWidth: '0px', height: '52px'}}
                        variant="contained"
                        color="primary"
                        disabled={this.state.waiting}
                        onClick={() => this.check_login(true)}
                    >
                        Sign in to Optumi
                    </Button>
                )}
                <DIV sx={{color: this.state.loginFailed ? 'error.main' : 'text.secondary'}}>
                    {this.getMessage()}
                    {this.state.showLoginHint && (
                        <DIV>
                            <br />
                            {"You will be directed to a new browser tab in a moment. If a tab doesn't open, check that your browser is not blocking popups and click "}
                            <Button
                                color='primary'
                                sx={{padding: '0px', minWidth: '36px', top: '-1px'}}
                                onClick={() => this.check_login(true)}
                            >
                                here
                            </Button>
                        </DIV>
                    )}
                    {this.state.showAllocatingHint && (
                        <DIV>
                            <br />
                            {"This may take a few minutes"}
                        </DIV>
                    )}
                </DIV>
                {/* <div dangerouslySetInnerHTML={{__html: this.fbWidget.node.innerHTML}} /> */}
            </Container>
            <DIV sx={{
                position: 'absolute',
                bottom: '10px',
                width: '100%',
                textAlign: 'center',
                color: 'text.secondary',
            }}>
                {Global.version}
            </DIV>
            <StyledDialog
                onClose={(event: object, reason: string) => void 0}
                open={this.state.packageString != ""}
            >
                <DialogTitle
                    sx={{
                        backgroundColor: 'var(--jp-layout-color2)',
                        height: '48px',
                        padding: '6px 30px',
                    }}>
                    <Header
                        title={this.state.downgrade ? "Switch to compatible JupyterLab extension" : "Upgrade JupyterLab extension"}
                        sx={{lineHeight: '24px'}}
                    />
                </DialogTitle>
                <ShadowedDivider />
                <DIV sx={{padding: '18px'}}>
                    <DialogContent sx={{padding: '6px 18px', lineHeight: '24px'}}>
                        <DIV>
                            {this.state.downgrade ? 
                                "Sorry, we've noticed an incompatibility between this JupyterLab extension version and our backend. To switch to a compatible JupyterLab extension run the command"
                            :
                                "We've made enhancements on the backend that require a new JupyterLab extension version. To upgrade your JupyterLab extension run the command"
                            }
                        </DIV>
                        <TEXTAREA
                            id="optumi-upgrade-string"
                            sx={{
                                fontFamily: 'var(--jp-code-font-family)',
                                width: '100%',
                                lineHeight: '18px',
                                marginTop: '6px',
                            }}
                            rows={1}
                            readOnly
                        >
                            {'pip install ' + this.state.packageString}
                        </TEXTAREA>
                        <DIV>
                            {'and restart JupyterLab.'}
                        </DIV>
                    </DialogContent>
                    <DialogActions sx={{padding: '12px 6px 6px 6px'}}>
                        <Button
                            variant='contained'
                            onClick={() => {
                                var copyTextarea: HTMLTextAreaElement = document.getElementById('optumi-upgrade-string') as HTMLTextAreaElement;
                                copyTextarea.focus();
                                copyTextarea.select();

                                try {
                                    document.execCommand('copy');
                                } catch (err) {
                                    console.log(err);
                                }
                            }}
                            color={'primary'}
                        >
                            Copy command
                        </Button>
                        <Button
                            variant='contained'
                            onClick={() => {
                                this.safeSetState({loginFailed: false, packageString: "", downgrade: false, loginFailedMessage: ""});
                            }}
                            color={'secondary'}
                        >
                            Close
                        </Button>
                    </DialogActions>
                </DIV>
            </StyledDialog>
        </>;
	}

	// Try to log into the REST interface and update state according to response
	private async login() {
		this.setState({ showLoginHint: false });
		var timeout = setTimeout(() => this.setState({ showAllocatingHint: true }), 30000);
		const settings = ServerConnection.makeSettings();
		const url = settings.baseUrl + "optumi/login";
		const init = {
			method: 'GET',
		};
		ServerConnection.makeRequest(
			url,
			init, 
			settings
		).then((response: Response) => {
			if (response.status !== 200 && response.status !== 201) {
				clearTimeout(timeout)
				this.safeSetState({ loginFailed: true, loginFailedMessage: "Unable to restore context", waiting: false, showLoginHint: false, showAllocatingHint: false });
				throw new ServerConnection.ResponseError(response);
			}
			return response.json();
		}).then((body: any) => {
			if (body) {
				clearTimeout(timeout)
				if (body.loginFailed) {
					this.newTab = null;
					if (body.message == 'Version exchange failed') {
						var rawVersion = body.loginFailedMessage;
						var split = rawVersion.split('-')[0].split('.');
						const downgrade = Global.version.split('.')[1] > split[1];
						var packageString = '"jupyterlab-optumi>=' + split[0] + '.' + split[1] + '.0,' + '<' + split[0] + '.' + (+split[1] + 1) + '.0"'
						this.safeSetState({ loginFailed: body.loginFailed || false, packageString: packageString, downgrade: downgrade, waiting: false, showLoginHint: false, showAllocatingHint: false });
					} else {
						this.setState({ loginFailed: body.loginFailed || false, loginFailedMessage: body.loginFailedMessage || "", waiting: false, showLoginHint: false, showAllocatingHint: false })
					}
				} else {
					try {
						var user = User.handleLogin(body);
						Global.user = user;
					} catch (err) {
						console.error(err);
						this.safeSetState({ loginFailed: true, loginFailedMessage: "Unable to restore context", waiting: false, showLoginHint: false, showAllocatingHint: false });
					}
				}
			}
		});
	}

	private newTab: Window = null;
	private loginHintTimeout: NodeJS.Timeout = null;
    private async check_login(first: boolean = false) {
		// If the user has not logged in in 10 minutes after the new tab pops up, we time out
		if (this.state.progress == 'Logging in...' && new Date().getTime() - this.lastLoginAttempt.getTime() > 600000) {
			this.safeSetState({ loginFailed: true, loginFailedMessage: "Timed out", waiting: false, showLoginHint: false });
		}
		if (first && (new Date().getTime() - this.lastLoginAttempt.getTime() > 5000)) {
			this.newTab = window.open(window.location.origin + '/optumi/oauth-login')
			if(!this.newTab || this.newTab.closed || typeof this.newTab.closed=='undefined')  {
				this.setState({ showLoginHint: true });
				this.newTab = null;
				return;
			}
			this.lastLoginAttempt = new Date();
			this.safeSetState({ progress: 'Logging in...', waiting: true, loginFailed: false, loginFailedMessage: ""});
			this.loginHintTimeout = setTimeout(() => this.setState({ showLoginHint: true }), 6000);
		}

        const settings = ServerConnection.makeSettings();
		const url = settings.baseUrl + "optumi/get-login-progress";
		const init = {
			method: 'GET',
		};
		ServerConnection.makeRequest(
			url,
			init, 
			settings
		).then((response: Response) => {
			if (response.status == 204) {
                return;
			}
			if (response.status !== 200 && response.status !== 201) {
				throw new ServerConnection.ResponseError(response);
			}
			return response.text();
		}).then((body: string) => {
			if (body) {
				if (body == 'Allocating...') {
					if (this.newTab) {
						clearTimeout(this.loginHintTimeout)
						this.loginHintTimeout = null;
						this.newTab.close();
						this.newTab = null;
						this.login();
					}
				}
				this.setState({progress: body})
			}
			if (Global.user == null) setTimeout(() => { this.check_login(); }, 500);
		});
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
		this.observer.observe(document.getElementById('optumi/Optumi'), { attributes : true, attributeFilter : ['class'] });
	}

	// Will be called automatically when the component is unmounted
	public componentWillUnmount = () => {
		this._isMounted = false;
		this.observer.disconnect();
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
