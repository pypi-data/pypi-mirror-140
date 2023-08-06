/*
**  Copyright (C) Optumi Inc - All rights reserved.
**
**  You may only use this code under license with Optumi Inc and any distribution or modification is strictly prohibited.
**  To receive a copy of the licensing terms please write to contact@optumi.com or visit us at http://www.optumi.com.
**/

import * as React from 'react';
import { DIV, Global } from '../../Global';

import { SxProps, Theme } from '@mui/system';
import { Button, Divider, IconButton } from '@mui/material';
import { GetApp as GetAppIcon, Delete as DeleteIcon } from '@mui/icons-material';

import { ServerConnection } from '@jupyterlab/services';

// import { ChangePasswordPopup } from './ChangePasswordPopup';
import { CreditBucketCheckoutForm } from './CreditBucketCheckoutForm';
import { Header, Switch, TextBox, TextBoxDropdown } from '../../core';
import FormatUtils from '../../utils/FormatUtils';
import DataConnectorBrowser, { DataConnectorMetadata } from '../deploy/dataConnectorBrowser/DataConnectorBrowser';
import { AmazonS3ConnectorPopup } from '../deploy/AmazonS3ConnectorPopup';
import { GoogleCloudStorageConnectorPopup } from '../deploy/GoogleCloudStorageConnectorPopup';
import { GoogleDriveConnectorPopup } from '../deploy/GoogleDriveConnectorPopup';
import { KaggleConnectorPopup } from '../deploy/KaggleConnectorPopup';
import { WasabiConnectorPopup } from '../deploy/WasabiConnectorPopup';
// import { PhoneTextBox } from '../../core/PhoneTextBox';
import { AzureBlobStorageConnectorPopup } from '../deploy/AzureBlobStorageConnector';
import { FileMetadata } from '../deploy/fileBrowser/FileBrowser';
import { FileTree } from '../FileTree';
import { BillingType } from '../../models/User';
import { MeteredBilling } from './MeteredBilling';
import FileServerUtils from '../../utils/FileServerUtils';

import moment from 'moment';
import { PhoneNumberFormat, PhoneNumberUtil } from 'google-libphonenumber';
import { FreeTrial } from './Freetrial';

// Properties from parent
interface IAccountPreferencesSubMenuProps {
    phoneValidOnBlur?: (valid: boolean) => void
	sx?: SxProps<Theme>
}

const emUpSub = 'Upgrade subscription to unlock'

const LABEL_WIDTH = '80px'

interface IAccountPreferencesSubMenuState {
    switchKey: number
}

export class AccountPreferencesSubMenu extends React.Component<IAccountPreferencesSubMenuProps, IAccountPreferencesSubMenuState> {

    constructor(props: IAccountPreferencesSubMenuProps) {
        super(props);
        this.state = {
            // We need to increment this when the user changes his number so the switch will be enabled/disabled properly
            switchKey: 0
        }
    }

    // private getPasswordValue(): string { return '******' }
    // private savePasswordValue(password: string) {
    //     Global.user.changePassword("", "", password);
    // }
    
    public render = (): JSX.Element => {
		if (Global.shouldLogOnRender) console.log('ComponentRender (' + new Date().getSeconds() + ')');
        const phoneUtil = PhoneNumberUtil.getInstance();
        return (
            <>
                <DIV sx={Object.assign({padding: '6px'}, this.props.sx)}>
                    {/* <ResourceTextBox<string>
                        getValue={this.getNameValue}
                        label='Name'
                        editPressRequired
                    /> */}
                    {/* <DIV sx={{display: 'inline-flex', width: '100%'}}>
                        <TextBox<string>
                            sx={{flexGrow: 1}}
                            getValue={this.getPasswordValue}
                            saveValue={this.savePasswordValue}
                            label='Password'
                            labelWidth={LABEL_WIDTH}
                        />
                        <ChangePasswordPopup sx={{margin: '8px 0px', height: '20px', fontSize: '12px', lineHeight: '12px'}}/>
                    </DIV> */}
                    {/* <PhoneTextBox
                        getValue={() => Global.user.phoneNumber}
                        saveValue={(phoneNumber: string) => {
                            if (phoneNumber == '') Global.user.notificationsEnabled = false;
                            Global.user.phoneNumber = phoneNumber;
                            // We need to update so the switch below will be updated properly
                            this.setState({ switchKey: this.state.switchKey+1 });
                        }}
                        validOnBlur={this.props.phoneValidOnBlur}
                        label='Phone'
                        labelWidth={LABEL_WIDTH}
                    /> */}
                    <Switch
                        key={this.state.switchKey}
                        getValue={() => Global.user.notificationsEnabled }
                        saveValue={(notificationsEnabled: boolean) => { Global.user.notificationsEnabled = notificationsEnabled }}
                        label={'Enable SMS notifications to ' + phoneUtil.format(phoneUtil.parse(Global.user.phoneNumber, 'US'), PhoneNumberFormat.INTERNATIONAL)}
                        // disabled={Global.user.phoneNumber == ''}
                        labelBefore
                        flip
                    />
                    <Switch
                        getValue={() => Global.user.compressFilesEnabled}
                        saveValue={(compressFilesEnabled: boolean) => { Global.user.compressFilesEnabled = compressFilesEnabled }}
                        label='Compress my files before uploading'
                        labelBefore
                        flip
                    />
                    <Switch
                        getValue={() => Global.user.snapToInventoryEnabled}
                        saveValue={(snapToInventoryEnabled: boolean) => { Global.user.snapToInventoryEnabled = snapToInventoryEnabled }}
                        label='Snap resource selection sliders to existing inventory'
                        labelBefore
                        flip
                    />
                    {Global.user.showDownloadAllButtonEnabled && (
                        <Button 
                            variant="outlined"
                            color="primary"
                            startIcon={<GetAppIcon />}
                            sx={{width: '100%'}}
                            onClick={async () => {
                                const data = [];
                                for (let app of Global.user.appTracker.finishedJobsOrSessions) {
                                    const machine = app.machine;
                                    data.push(
                                        [
                                            this.stringToCSVCell(app.name),
                                            this.stringToCSVCell(app.annotationOrRunNum),
                                            app.timestamp,
                                            app.getTimeElapsed(),
                                            app.interactive ? 'N/A' : app.notebook.metadata.papermill.duration,
                                            app.getCost(),
                                            app.getAppMessage(),
                                            machine.name,
                                            machine.computeCores,
                                            FormatUtils.styleCapacityUnitValue()(machine.memorySize),
                                            FormatUtils.styleCapacityUnitValue()(machine.storageSize),
                                            machine.graphicsNumCards > 0 ? (machine.graphicsNumCards + ' ' + machine.graphicsCardType) : 'None',
                                            app.uuid,
                                        ]
                                    );
                                    
                                    var link = document.createElement("a");
                                    var blob = new Blob([JSON.stringify(app.machine)], {
                                        type: "text/plain;charset=utf-8"
                                    });
                                    link.setAttribute("href", window.URL.createObjectURL(blob));
                                    link.setAttribute("download", app.uuid + ".txt");
                                    document.body.appendChild(link); // Required for FF
                                    link.click();

                                    await new Promise(resolve => setTimeout(resolve, 100));

                                    // const ipynbContent = 'data:text/plain;charset=utf-8,'
                                    //     + JSON.stringify(app.notebook);
                                    var link = document.createElement("a");
                                    var blob = new Blob([JSON.stringify(app.notebook)], {
                                        type: "text/plain;charset=utf-8"
                                    });
                                    link.setAttribute("href", window.URL.createObjectURL(blob));
                                    link.setAttribute("download", app.uuid + ".ipynb");
                                    document.body.appendChild(link); // Required for FF
                                    link.click();

                                    await new Promise(resolve => setTimeout(resolve, 100));
                                }
            
                                const headers = [
                                    ["Name", "Annotation", "Start Time", "Duration (total)", "Duration (notebook)", "Cost", "Status", "Machine", "Cores", "RAM", "Disk", "GPUs", "UUID"]
                                ];
            
                                var link = document.createElement("a");
                                var blob = new Blob([headers.map(e => e.join(",")).join("\n") + '\n' + data.map(e => e.join(",")).join("\n") + '\n'], {
                                    type: "data:text/csv;charset=utf-8,"
                                });
                                link.setAttribute("href", window.URL.createObjectURL(blob));
                                link.setAttribute("download", "run_history.csv");
                                document.body.appendChild(link); // Required for FF
                                link.click();
                            }
                        }>
                            Download all runs
                        </Button>
                    )}
                </DIV>
            </>
        )
    }

    public stringToCSVCell(str: string): string {
        var s = "\"";
        for(let nextChar of str) {
            s += nextChar;
            if (nextChar == '"')
                s += "\"";
        }
        s += "\"";
        return s;
    }

    public shouldComponentUpdate = (nextProps: IAccountPreferencesSubMenuProps, nextState: IAccountPreferencesSubMenuState): boolean => {
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

// Properties from parent
interface IAccountLimitsSubMenuProps {
    // phoneValidOnBlur?: (valid: boolean) => void
	sx?: SxProps<Theme>
}

interface IAccountLimitsSubMenuState {
    holdoverFocused: boolean;
    budgetFocused: boolean;
    recsFocused: boolean;
}

export class AccountLimitsSubMenu extends React.Component<IAccountLimitsSubMenuProps, IAccountLimitsSubMenuState> {
    private _isMounted = false

    constructor(props: IAccountLimitsSubMenuProps) {
        super(props);
        this.state = {
            holdoverFocused: false,
            budgetFocused: false,
            recsFocused: false,
        }
    }
    private getUserBudgetValue(): number { return Global.user.userBudget }
    private saveUserBudgetValue(userBudget: number) { Global.user.userBudget = userBudget }

    private getMaxJobsValue(): number { return Global.user.maxJobs }
    private saveMaxJobsValue(value: number) { Global.user.maxJobs = value }

    private getMaxMachinesValue(): number { return Global.user.maxMachines }
    private saveMaxMachinesValue(value: number) { Global.user.maxMachines = value }

    private getUserHoldoverTimeValue(): number { return Global.user.userHoldoverTime }
    private saveUserHoldoverTimeValue(userHoldoverTime: number) { Global.user.userHoldoverTime = userHoldoverTime }

    public render = (): JSX.Element => {
		if (Global.shouldLogOnRender) console.log('ComponentRender (' + new Date().getSeconds() + ')');
        return <>
            <DIV sx={Object.assign({padding: '6px'}, this.props.sx)}>
                {Global.user.userExpertise > 0 ? (<TextBox<number>
                    getValue={this.getUserBudgetValue}
                    saveValue={this.saveUserBudgetValue}
                    styledUnitValue={(value: number) => '$' + value.toFixed(2)}
                    unstyleUnitValue={(value: string) => { return value.replace('$', '').replace('.', '').replace(/\d/g, '').length > 0 ? Number.NaN : Number.parseFloat(value.replace('$', '')); }}
                    label='Budget'
                    labelWidth={LABEL_WIDTH}
                    onFocus={() => this.safeSetState({budgetFocused: true})}
                    onBlur={() => this.safeSetState({budgetFocused: false})}
                    helperText={this.state.budgetFocused ? `Must be between $1 and $${Global.user.maxBudget}` : 'Max monthly spend'}
                    minValue={1}
                    maxValue={Global.user.maxBudget}
                    // disabledMessage={Global.user.userExpertise < 2 ? emUpSub : ''}
                />) : (<></>)}
                <TextBox<number>
                    getValue={this.getMaxJobsValue}
                    saveValue={this.saveMaxJobsValue}
                    unstyleUnitValue={(value: string) => { return value.replace(/\d/g, '').length > 0 ? Number.NaN : Number.parseFloat(value); }}
                    label='Jobs/Sessions'
                    labelWidth={LABEL_WIDTH}
                    helperText={'Max combined number of concurrent jobs and sessions'}
                    disabledMessage={emUpSub}
                />
                <TextBox<number>
                    getValue={this.getMaxMachinesValue}
                    saveValue={this.saveMaxMachinesValue}
                    unstyleUnitValue={(value: string) => { return value.replace(/\d/g, '').length > 0 ? Number.NaN : Number.parseFloat(value); }}
                    label='Machines'
                    labelWidth={LABEL_WIDTH}
                    helperText='Max number of concurrent machines'
                    disabledMessage={emUpSub}
                />
                <TextBoxDropdown
                    getValue={this.getUserHoldoverTimeValue}
                    saveValue={this.saveUserHoldoverTimeValue}
                    unitValues={[
                        {unit: 'seconds', value: 1},
                        {unit: 'minutes', value: 60},
                        {unit: 'hours', value: 3600},
                    ]}
                    label='Auto-release'
                    labelWidth={LABEL_WIDTH}
                    onFocus={() => this.safeSetState({holdoverFocused: true})}
                    onBlur={() => this.safeSetState({holdoverFocused: false})}
                    helperText={this.state.holdoverFocused ? `Must be between 0 seconds and ${Global.user.maxHoldoverTime / 3600} hours` : 'Time before releasing idle machines'}
                    minValue={0}
                    maxValue={Global.user.maxHoldoverTime}
                />
            </DIV>
        </>;
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

    public shouldComponentUpdate = (nextProps: IAccountLimitsSubMenuProps, nextState: IAccountLimitsSubMenuState): boolean => {
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

// Properties from parent
interface IAccountBillingSubMenuProps {
	sx?: SxProps<Theme>
    balance: number
    machineCost: number
    serviceFeeCost: number
    storageCost: number
    egressCost: number
}

interface IAccountBillingSubMenuState {
    balance: number
}

export class AccountBillingSubMenu extends React.Component<IAccountBillingSubMenuProps, IAccountBillingSubMenuState> {
    private _isMounted = false;
    private polling = false;
    private timeout: NodeJS.Timeout

    constructor(props: IAccountBillingSubMenuProps) {
        super(props);
        this.state = {
            balance: 0,
        }
    }

    public render = (): JSX.Element => {
		if (Global.shouldLogOnRender) console.log('ComponentRender (' + new Date().getSeconds() + ')');
        return (
            <>
                <DIV sx={Object.assign({padding: '6px'}, this.props.sx)}>
                    {Global.user.billingType == BillingType.CREDIT_BUCKET ? (
                        <>
                            <DIV sx={{display: 'inline-flex', width: '100%', padding: '3px 0px'}}>
                                <DIV 
                                    sx={{
                                    lineHeight: '24px',
                                    margin: '0px 12px',
                                    flexGrow: 1,
                                }}
                                >
                                    {'Remaining balance'}
                                </DIV>
                                <DIV sx={{padding: '0px 6px 0px 6px'}}>
                                    {'$' + (-this.state.balance).toFixed(2)}
                                </DIV>
                            </DIV>
                            <DIV sx={{width: '250px'}}>
                                <CreditBucketCheckoutForm />
                            </DIV>
                        </>
                    ) : (
                        <>
                            {Global.user.subscriptionActive ? (
                                <MeteredBilling 
                                    machineCost={this.props.machineCost}
                                    serviceFeeCost={this.props.serviceFeeCost}
                                    storageCost={this.props.storageCost}
                                    egressCost={this.props.egressCost}
                                />
                            ) : (
                                <FreeTrial balance={this.props.balance}/>
                            )}
                        </>
                    )}
                </DIV>
            </>
        )
    }

    private async receiveUpdate() {
		const settings = ServerConnection.makeSettings();
        const url = settings.baseUrl + "optumi/get-balance";
        const now = new Date();
        const epoch = new Date(0);
		const init: RequestInit = {
			method: 'POST',
			body: JSON.stringify({
				startTime: epoch.toISOString(),
				endTime: now.toISOString(),
			}),
		};
		ServerConnection.makeRequest(
			url,
			init, 
			settings
		).then((response: Response) => {
			if (this.polling) {
				// If we are polling, send a new request in 2 seconds
                if (Global.shouldLogOnPoll) console.log('FunctionPoll (' + new Date().getSeconds() + ')');
				this.timeout = setTimeout(() => this.receiveUpdate(), 2000);
			}
			Global.handleResponse(response);
			return response.json();
		}).then((body: any) => {
			if (body) {
                this.safeSetState({ balance: body.balance });
			}
        });
    }
    
    // Will be called automatically when the component is mounted
	public componentDidMount = () => {
        this._isMounted = true;
        this.polling = true;
        this.receiveUpdate();
	}

	// Will be called automatically when the component is unmounted
	public componentWillUnmount = () => {
        this._isMounted = false;
        this.polling = false;
        if (this.timeout != null) clearTimeout(this.timeout)
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

    public shouldComponentUpdate = (nextProps: IAccountBillingSubMenuProps, nextState: IAccountBillingSubMenuState): boolean => {
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

// Properties from parent
interface IAccountConnectorsSubMenuProps {
	sx?: SxProps<Theme>
}

interface IAccountConnectorsSubMenuState {
    dataConnectors: DataConnectorMetadata[],
    browserKey: number,
}

export class AccountConnectorsSubMenu extends React.Component<IAccountConnectorsSubMenuProps, IAccountConnectorsSubMenuState> {
    private _isMounted = false

    constructor(props: IAccountConnectorsSubMenuProps) {
        super(props);
        this.state = {
            dataConnectors: [],
            browserKey: 0,
        }
    }

    // Use a key to force the data connector browser to refresh
    private forceNewBrowser = () => {
        this.safeSetState({ browserKey: this.state.browserKey + 1 })
    }

    public request = async () => {
        const settings = ServerConnection.makeSettings();
		const url = settings.baseUrl + 'optumi/get-data-connectors'
		return ServerConnection.makeRequest(url, {}, settings).then(response => {
			if (response.status !== 200) throw new ServerConnection.ResponseError(response);
			return response.json()
		})
    }

    public render = (): JSX.Element => {
		if (Global.shouldLogOnRender) console.log('ComponentRender (' + new Date().getSeconds() + ')');
        return (
            <>
                <DIV sx={Object.assign({}, this.props.sx)}>
                    <DIV sx={{display: 'inline-flex', margin: '6px'}}>
                        <Header title='Existing connectors' sx={{ lineHeight: '24px', margin: '6px 6px 6px 11px' }} />
                    </DIV>
                    <Divider />
                    <DataConnectorBrowser
                        key={this.state.browserKey}
                        sx={{
                            maxHeight: 'calc(100% - 60px - 2px)',
                        }}
                        handleDelete={(dataConnectorMetadata: DataConnectorMetadata) => {
                            const settings = ServerConnection.makeSettings();
                            const url = settings.baseUrl + "optumi/remove-data-connector";
                            const init: RequestInit = {
                                method: 'POST',
                                body: JSON.stringify({
                                    name: dataConnectorMetadata.name,
                                }),
                            };
                            ServerConnection.makeRequest(
                                url,
                                init, 
                                settings
                            ).then((response: Response) => {
                                Global.handleResponse(response);
                            }).then(() => {
                                var newDataConnectors = [...this.state.dataConnectors]
                                newDataConnectors = newDataConnectors.filter(dataConnector => dataConnector.name !== dataConnectorMetadata.name)
                                this.safeSetState({dataConnectors: newDataConnectors})
                                this.forceNewBrowser()
                            }).then(() => Global.dataConnectorChange.emit(void 0));                   
                        }}
                    />
                    <Divider sx={{marginTop: '33px'}}/>
                    <DIV sx={{display: 'inline-flex', margin: '6px'}}>
                        <Header title='New connectors' sx={{ lineHeight: '24px', margin: '6px 6px 6px 11px'  }} />
                    </DIV>
                    <Divider />
                    <DIV sx={{marginBottom: '6px'}} />
                    <AmazonS3ConnectorPopup onClose={this.forceNewBrowser} />
                    <AzureBlobStorageConnectorPopup onClose={this.forceNewBrowser} />
                    <GoogleCloudStorageConnectorPopup onClose={this.forceNewBrowser} />
                    <GoogleDriveConnectorPopup onClose={this.forceNewBrowser} />
                    <KaggleConnectorPopup onClose={this.forceNewBrowser} />
                    <WasabiConnectorPopup onClose={this.forceNewBrowser} />
                </DIV>
            </>
        )
    }

    public componentDidMount = () => {
        this._isMounted = true
        this.request().then(json => this.safeSetState({dataConnectors: json.connectors}))
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

    public shouldComponentUpdate = (nextProps: IAccountConnectorsSubMenuProps, nextState: IAccountConnectorsSubMenuState): boolean => {
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

// Properties from parent
interface IAccountFilesSubMenuProps {
	sx?: SxProps<Theme>
}

interface IAccountFilesSubMenuState {}

export class AccountFilesSubMenu extends React.Component<IAccountFilesSubMenuProps, IAccountFilesSubMenuState> {
    constructor(props: IAccountFilesSubMenuProps) {
        super(props);
        this.state = {
            files: [],
            appsToFiles: new Map(),
            filesToApps: new Map(),
        }
    }

    public render = (): JSX.Element => {
		if (Global.shouldLogOnRender) console.log('ComponentRender (' + new Date().getSeconds() + ')');
        const files = Global.user.fileTracker.files;
        var sorted: FileMetadata[] = !files ? [] : files.sort(FileServerUtils.sortFiles);
        const total = Global.user.fileTracker.total
        return <>
            <DIV sx={Object.assign({padding: '20px 6px 6px 20px'}, this.props.sx)}>
                <DIV>
                    Listed files are securely stored in the Optumi platform. If you want to delete a file click on the associated trash can.
                    {total > 0 && <>
                        <br />
                        <br />
                        Total used storage: {FormatUtils.styleCapacityUnitValue()(Global.user.fileTracker.total)}
                    </>}
                </DIV>
                <FileTree
                    files={sorted}
                    fileTitle={file => (
`Name: ${file.name}
${file.size === null ? '' : `Size: ${FormatUtils.styleCapacityUnitValue()(file.size)} (${file.size} bytes)
`}${file.path === '' ? '' : `Path: ${file.path.replace(file.name, '').replace(/\/$/, '')}
`}Modified: ${moment(file.last_modified).format('YYYY-MM-DD hh:mm:ss')}`
                    )}
                    fileHidableIcon={file => ({
                        width: 72,
                        height: 36,
                        icon: (
                            <>
                                <IconButton
                                    size='large'
                                    onClick={() => this.downloadFile(file)}
                                    sx={{ width: '36px', height: '36px', padding: '3px' }}
                                >
                                    <GetAppIcon sx={{ width: '30px', height: '30px', padding: '3px' }} />
                                </IconButton>
                                <IconButton
                                    size='large'
                                    onClick={() => this.deleteFile(file)}
                                    sx={{ width: '36px', height: '36px', padding: '3px' }}
                                >
                                    <DeleteIcon sx={{ width: '30px', height: '30px', padding: '3px' }} />
                                </IconButton>
                            </>
                        ),
                    })}
                    directoryHidableIcon={path => ({
                        width: 72,
                        height: 36,
                        icon: (
                            <>
                                <IconButton
                                    size='large'
                                    onClick={() => this.downloadDirectory(path)}
                                    sx={{ width: '36px', height: '36px', padding: '3px' }}
                                >
                                    <GetAppIcon sx={{ width: '30px', height: '30px', padding: '3px' }} />
                                </IconButton>
                                <IconButton
                                    size='large'
                                    onClick={() => this.deleteDirectory(path)}
                                    sx={{ width: '36px', height: '36px', padding: '3px' }}
                                >
                                    <DeleteIcon sx={{ width: '30px', height: '30px', padding: '3px' }} />
                                </IconButton>
                            </>
                        ),
                    })}
                />
            </DIV>
        </>;
    }

    private async deleteFile(file: FileMetadata) {
        Global.user.fileTracker.deleteFiles([file]);
    }

    private async downloadFile(file: FileMetadata) {
		Global.user.fileTracker.downloadFiles(file.path, [file], false);
    }

    private async deleteDirectory(path: string) {
        let filesToDelete: FileMetadata[] = []
        for (let file of Global.user.fileTracker.files) {
            if (file.path.startsWith('~/' + path)) {
                filesToDelete.push(file)
            }
        }
        Global.user.fileTracker.deleteFiles(filesToDelete);
    }

    private async downloadDirectory(path: string) {
        let filesToDownload: FileMetadata[] = []
        for (let file of Global.user.fileTracker.files) {
            if (file.path.startsWith('~/' + path)) {
                filesToDownload.push(file)
            }
        }
        Global.user.fileTracker.downloadFiles(path, filesToDownload, false, [], path);
    }

    private handleFilesChange = () => this.forceUpdate();

    // Will be called automatically when the component is mounted
	public componentDidMount = () => {
        if (Global.user != null) Global.user.fileTracker.getFilesChanged().connect(this.handleFilesChange);
	}

	// Will be called automatically when the component is unmounted
	public componentWillUnmount = () => {
        if (Global.user != null) Global.user.fileTracker.getFilesChanged().disconnect(this.handleFilesChange);
    }

    public shouldComponentUpdate = (nextProps: IAccountFilesSubMenuProps, nextState: IAccountFilesSubMenuState): boolean => {
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
export class TeamSubMenu extends React.Component<IAccountFilesSubMenuProps, IAccountFilesSubMenuState> {
    public render = (): JSX.Element => {
		if (Global.shouldLogOnRender) console.log('ComponentRender (' + new Date().getSeconds() + ')');
        return (
            <Header title='Members' />
        )
    }
}
