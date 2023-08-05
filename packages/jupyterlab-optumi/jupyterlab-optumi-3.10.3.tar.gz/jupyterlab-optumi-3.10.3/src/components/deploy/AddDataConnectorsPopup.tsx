/*
**  Copyright (C) Optumi Inc - All rights reserved.
**
**  You may only use this code under license with Optumi Inc and any distribution or modification is strictly prohibited.
**  To receive a copy of the licensing terms please write to contact@optumi.com or visit us at http://www.optumi.com.
**/

import * as React from 'react'
import { DIV, Global } from '../../Global';

import { SxProps, Theme } from '@mui/system';
import { Button, Dialog, DialogTitle, Divider, IconButton } from '@mui/material';
import { withStyles } from '@mui/styles';
import { Close, OpenInNew } from '@mui/icons-material';

import { ShadowedDivider } from '../../core';
import DataConnectorBrowser, { DataConnectorMetadata } from './dataConnectorBrowser/DataConnectorBrowser';
import { Page } from '../UserDialog';

const StyledDialog = withStyles({
    paper: {
        width: 'calc(min(80%, 600px + 150px + 2px))',
        // width: '100%',
        height: '80%',
        overflowY: 'visible',
        maxWidth: 'inherit',
    },
})(Dialog);

const StyledButton = withStyles({
   root: {
       height: '20px',
       padding: '0px',
       fontSize: '12px',
       lineHeight: '12px',
       minWidth: '0px',
       margin: '0px 6px 6px 6px',
       width: '100%',
    },
   label: {
       height: '20px',
   },
})(Button);

interface IProps {
    sx?: SxProps<Theme>
    onOpen?: () => void
    onClose?: () => void
    onDataConnectorsAdded: (paths: DataConnectorMetadata[]) => void
    openUserDialogTo?: (page: number) => Promise<void>
}

interface IState {
    open: boolean,
}

export class AddDataConnectorsPopup extends React.Component<IProps, IState> {
    private _isMounted = false

    private getSelectedDataConnectors: () => DataConnectorMetadata[] = () => []

    constructor(props: IProps) {
        super(props);
		this.state = {
            open: false,
		};
    }

    private handleClickOpen = () => {
        if (this.props.onOpen) this.props.onOpen()
		this.safeSetState({ open: true });
	}

	private handleClose = () => {
        this.safeSetState({ open: false });
        if (this.props.onClose) this.props.onClose()
    }
    
    private handleAdd = () => {
        this.props.onDataConnectorsAdded(this.getSelectedDataConnectors())
        // console.log(this.getSelectedFiles())
        this.handleClose()
    }

    private handleKeyDown = (event: KeyboardEvent) => {
        if (!this.state.open || document.getElementsByClassName('MuiDialog-root').length > 1) return; // This means theres another popup open, so it expects the key input
        // The enter has to be a timeout because without it the file gets added but the popup doesn't close
        if (event.key === 'Enter') setTimeout(() => this.handleAdd(), 0);
        if (event.key === 'Escape') this.handleClose();
    }

    public render = (): JSX.Element => {
        if (Global.shouldLogOnRender) console.log('ComponentRender (' + new Date().getSeconds() + ')');
        return (
            <DIV sx={Object.assign({display: 'inline-flex', width: '50%'}, this.props.sx)} >
                <StyledButton
                    onClick={this.handleClickOpen}
                    variant='contained'
                    disableElevation
                    color='primary'
                >
                    + Connector
                </StyledButton>
                <StyledDialog
					open={this.state.open}
					onClose={this.handleClose}
                    scroll='paper'
				>
					<DialogTitle sx={{
                        display: 'inline-flex',
                        height: '60px',
                        padding: '6px',
                    }}>
                        <DIV sx={{
                            display: 'inline-flex',
                            width: '100%',
                            fontSize: '16px',
                            fontWeight: 'bold',
                            paddingRight: '12px', // this is 6px counteracting the DialogTitle padding and 6px aligning the padding to the right of the tabs
                        }}>
                            <DIV sx={{margin: 'auto 12px'}}>
            					Select data connectors
                            </DIV>
                        </DIV>
                        <DIV sx={{flexGrow: 1}} />
                        <DIV>
                            <Button
                                disableElevation
                                sx={{ height: '36px', margin: '6px' }}
                                variant='contained'
                                color='primary'
                                onClick={this.handleAdd}
                            >
                                Add
                            </Button>
                        </DIV>
                        <IconButton
                            size='large'
                            onClick={this.handleClose}
                            sx={{
                                display: 'inline-block',
                                width: '36px',
                                height: '36px',
                                padding: '3px',
                                margin: '6px',
                            }}
                        >
                            <Close
                                sx={{
                                    width: '30px',
                                    height: '30px',
                                    padding: '3px',
                                }}
                            />
                        </IconButton>
					</DialogTitle>
                    <ShadowedDivider />
                    <DataConnectorBrowser sx={{flexGrow: 1, height: '100%', maxHeight: 'calc(100% - 60px - 60px - 2px)'}} onAdd={this.handleAdd} getSelected={(getSelectedDataConnectors: () => DataConnectorMetadata[]) => this.getSelectedDataConnectors = getSelectedDataConnectors} />
                    <Divider />
                    <DIV sx={{display: 'inline-flex', margin: '6px 100px', height: '60px'}}>
                        <DIV sx={{display: 'inline-flex', flexGrow: 1, margin: 'auto'}}>
                            <DIV className='jp-s3-logo' sx={{width: '30px', height: '30px', margin: '0px 12px'}} style={{backgroundSize: 'contain'}} />
                            <DIV className='jp-drive-logo' sx={{width: '30px', height: '30px', margin: '0px 12px'}} style={{backgroundSize: 'contain'}} />
                            <DIV className='jp-cloud-logo' sx={{width: '30px', height: '30px', margin: '0px 12px'}} style={{backgroundSize: 'contain'}} />
                            <DIV className='jp-kaggle-logo' sx={{width: '30px', height: '30px', margin: '0px 12px'}} style={{backgroundSize: 'contain'}} />
                            <DIV className='jp-wasabi-logo' sx={{width: '30px', height: '30px', margin: '0px 12px'}} style={{backgroundSize: 'contain'}} />
                        </DIV>
                        <Button
                            disableElevation
                            sx={{ height: '36px', margin: 'auto 12px'}}
                            variant='contained'
                            color='primary'
                            onClick={() => {
                                this.props.openUserDialogTo(Page.CONNECTORS)
                                this.safeSetState({open: false})
                            }}
                            endIcon={<OpenInNew />}
                        >
                            Create connectors
                        </Button>
                    </DIV>
                </StyledDialog>
            </DIV>
        );
    }

    public componentDidMount = () => {
        this._isMounted = true
        document.addEventListener('keydown', this.handleKeyDown, false)
    }

    public componentWillUnmount = () => {
        document.removeEventListener('keydown', this.handleKeyDown, false)
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
