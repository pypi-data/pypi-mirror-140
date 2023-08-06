/*
**  Copyright (C) Optumi Inc - All rights reserved.
**
**  You may only use this code under license with Optumi Inc and any distribution or modification is strictly prohibited.
**  To receive a copy of the licensing terms please write to contact@optumi.com or visit us at http://www.optumi.com.
**/

// import * as React from 'react'

import { Global } from '../Global';

import { ServerConnection } from '@jupyterlab/services';
import { ISignal, Signal } from '@lumino/signaling';

import { App } from './application/App';
import { AppTracker } from './application/AppTracker';
import { Machines } from './Machines';
import { Machine } from './machine/Machine';
import { Page } from '../components/deploy/RequirementsBar';
import { FileTracker } from './FileTracker';
import { FileChecker } from './FileChecker';
import { EgressBucket } from './EgressBucket';
import { StorageBucket } from './StorageBucket';
// import { SnackbarKey } from 'notistack';
// import { IconButton } from '@mui/material';
// import { SubscribeButton } from '../core/SubscribeButton';
// import { Close } from '@mui/icons-material';
// import { Snackbar } from './Snackbar';
// import FormatUtils from '../utils/FormatUtils';

export enum BillingType {
	CREDIT_BUCKET = 'credit bucket',
	METERED_BILLING = 'metered subscription',
}

export class User {
	
	// Helper function to avoid duplicate code when logging in
	public static handleLogin(responseData: any): User {
        var machines: Machine[] = []
        for (var i = 0; i < responseData.machines.length; i++) {
            machines.push(Machine.parse(responseData.machines[i]));
        }
		var gpuGrid: Machine[][][] = []
        for (var i = 0; i < responseData.gpuGrid.length; i++) {
			var row = []
			for (var j = 0; j < responseData.gpuGrid[i].length; j++) {
				var bucket = []
				for (var k = 0; k < responseData.gpuGrid[i][j].length; k++) {
					bucket.push(Machine.parse(responseData.gpuGrid[i][j][k]));
				}
				row.push(bucket)
			}
			gpuGrid.push(row)
        }
		var cpuGrid: Machine[][][] = []
        for (var i = 0; i < responseData.cpuGrid.length; i++) {
			var row = []
			for (var j = 0; j < responseData.cpuGrid[i].length; j++) {
				var bucket = []
				for (var k = 0; k < responseData.cpuGrid[i][j].length; k++) {
					bucket.push(Machine.parse(responseData.cpuGrid[i][j][k]));
				}
				row.push(bucket)
			}
			cpuGrid.push(row)
        }

		var egressBuckets = []
		for (var i = 0; i < responseData.egressBuckets.length; i++) {
			egressBuckets.push({ limit: responseData.egressBuckets[i].limit.val, cost: responseData.egressBuckets[i].cost } as EgressBucket)
		}

		var storageBuckets = []
		for (var i = 0; i < responseData.storageBuckets.length; i++) {
			storageBuckets.push({ limit: responseData.storageBuckets[i].limit.val, cost: responseData.storageBuckets[i].cost } as EgressBucket)
		}

        const newUser = new User(
            responseData.newAgreement,
            responseData.name,
            responseData.phoneNumber,
            +responseData.intent,
            +responseData.userBudget,
            +responseData.maxBudget,
            +responseData.budgetCap,
            +responseData.userRate,
            +responseData.maxRate,
            +responseData.rateCap,
            +responseData.userAggregateRate,
            +responseData.maxAggregateRate,
            +responseData.aggregateRateCap,
            +responseData.userHoldoverTime,
            +responseData.maxHoldoverTime,
            +responseData.holdoverTimeCap,
            +responseData.userRecommendations,
            +responseData.maxRecommendations,
            +responseData.recommendationsCap,
            +responseData.maxJobs,
            +responseData.jobsCap,
            +responseData.maxMachines,
            +responseData.machinesCap,
            +responseData.userExpertise,
            responseData.billingType as BillingType,
			responseData.subscriptionActive,
			responseData.lastBillPaid,
			responseData.billingCycleAnchor ? new Date(responseData.billingCycleAnchor) : null,
			responseData.compressFilesEnabled,
			responseData.lastPage,
			responseData.stopJobPreventEnabled,
			responseData.deleteJobPreventEnabled,
			responseData.noRequirementsPreventEnabled,
			responseData.noFileUploadsPreventEnabled,
			responseData.startSessionPreventEnabled,
			responseData.notificationsEnabled,
			responseData.snapToInventoryEnabled,
			responseData.showMonitoringEnabled,
			responseData.showDownloadAllButtonEnabled,
			responseData.autoAddOnsEnabled,
			+responseData.egressTotal,
			+responseData.egressLimit,
			+responseData.egressMax,
			egressBuckets,
			storageBuckets, 
			+responseData.serviceFee,
			responseData.trialStart ? new Date(responseData.trialStart) : null,
			+responseData.credit,
            new AppTracker(),
			new FileTracker(),
			new FileChecker(),
            new Machines(machines, responseData.cpuLabels, cpuGrid, responseData.gpuLabels, gpuGrid, responseData.maxRate)
        );
        if (!newUser.unsignedAgreement) newUser.synchronize(responseData);
        return newUser;
	}
	
	private _deploySubMenuChanged = new Signal<this, User>(this);

	get deploySubMenuChanged(): ISignal<this, User> {
		return this._deploySubMenuChanged;
	}

	private _selectedSettingsSubMenuChanged = new Signal<this, User>(this);

	get selectedSettingsSubMenuChanged(): ISignal<this, User> {
		return this._selectedSettingsSubMenuChanged;
	}

	private _userInformationChanged = new Signal<this, User>(this);

	get userInformationChanged(): ISignal<this, User> {
		return this._userInformationChanged;
	}

    private _unsignedAgreement: boolean;

	private _name: string;
	private _phoneNumber: string;
	private _intent: number;
	private _userBudget: number;
	private _maxBudget: number;
	private _budgetCap: number;
    private _userRate: number;
	private _maxRate: number;
    private _rateCap: number;
    private _userAggregateRate: number;
	private _maxAggregateRate: number;
    private _aggregateRateCap: number;
    private _userHoldoverTime: number;
	private _maxHoldoverTime: number;
    private _holdoverTimeCap: number;
    private _userRecommendations: number;
	private _maxRecommendations: number;
    private _recommendationsCap: number;
    private _maxJobs: number;
    private _jobsCap: number;
    private _maxMachines: number;
    private _machinesCap: number;
	private _userExpertise: number;
	private _billingType: BillingType;
	private _subscriptionActive: boolean;
	private _lastBillPaid: boolean;
	private _billingCycleAnchor: Date;
	private _compressFilesEnabled: boolean;
	private _lastPage: number;
	private _stopJobPreventEnabled: boolean;
	private _deleteJobPreventEnabled: boolean;
	private _noRequirementsPreventEnabled: boolean;
	private _noFileUploadsPreventEnabled: boolean;
	private _startSessionPreventEnabled: boolean;
	private _notificationsEnabled: boolean;
	private _snapToInventoryEnabled: boolean;
	private _showMonitoringEnabled: boolean;
	private _showDownloadAllButtonEnabled: boolean;
	private _autoAddOnsEnabled: boolean;
	private _egressTotal: number;
	private _egressLimit: number;
	private _egressMax: number;
	private _egressBuckets: EgressBucket[];
	private _storageBuckets: StorageBucket[];
	private _serviceFee: number;
	private _trialStart: Date;
	private _credit: number;

	private _appTracker: AppTracker;
	private _fileTracker: FileTracker;
	private _fileChecker: FileChecker;
	private _machines: Machines;

	private _deploySubMenu: Page = Page.RESOURCES;

    constructor(unsignedAgreement: boolean, name: string, phoneNumber: string, intent: number, 
        userBudget: number, maxBudget: number, budgetCap: number, 
        userRate: number, maxRate: number, rateCap: number, 
        userAggregateRate: number, maxAggregateRate: number, aggregateRateCap: number, 
        userHoldoverTime: number, maxHoldoverTime: number, holdoverTimeCap: number, 
        userRecommendations: number, maxRecommendations: number, recommendationsCap: number, 
        maxJobs: number, jobsCap: number, 
        maxMachines: number, machinesCap: number, 
		userExpertise: number, billingType: BillingType, subscriptionActive: boolean, lastBillPaid: boolean, billingCycleAnchor: Date,
		compressFilesEnabled: boolean, lastPage: number, 
		stopJobPreventEnabled: boolean, deleteJobPreventEnabled: boolean, noRequirementsPreventEnabled: boolean, noFileUploadsPreventEnabled: boolean, 
		startSessionPreventEnabled: boolean, notificationsEnabled: boolean, snapToInventoryEnabled: boolean, showMonitoringEnabled: boolean, showDownloadAllButtonEnabled: boolean,
		autoAddOnsEnabled: boolean, egressTotal: number, egressLimit: number, egressMax: number,
		egressBuckets: EgressBucket[], storageBuckets: StorageBucket[], serviceFee: number, trialStart: Date, credit: number,
		appTracker: AppTracker, fileTracker: FileTracker, fileChecker: FileChecker, machines: Machines) {
        this._unsignedAgreement = unsignedAgreement === undefined ? true : unsignedAgreement;
        this._name = name;
        this._phoneNumber = phoneNumber;
		this._intent = intent;
        this._userBudget = userBudget;
        this._maxBudget = maxBudget;
        this._budgetCap = budgetCap;
        this._userRate = userRate;
        this._maxRate = maxRate;
        this._rateCap = rateCap;
        this._userAggregateRate = userAggregateRate;
        this._maxAggregateRate = maxAggregateRate;
        this._aggregateRateCap = aggregateRateCap;
        this._userHoldoverTime = userHoldoverTime;
        this._maxHoldoverTime = maxHoldoverTime;
        this._holdoverTimeCap = holdoverTimeCap;
        this._userRecommendations = userRecommendations;
        this._maxRecommendations = maxRecommendations;
        this._recommendationsCap = recommendationsCap;
        this._maxJobs = maxJobs;
        this._jobsCap = jobsCap;
        this._maxMachines = maxMachines;
        this._machinesCap = machinesCap;

		this._userExpertise = userExpertise;
		this._billingType = billingType;
		this._subscriptionActive = subscriptionActive;
		this._lastBillPaid = lastBillPaid;
		this._billingCycleAnchor = billingCycleAnchor;

		this._compressFilesEnabled = compressFilesEnabled;
		this._lastPage = lastPage;
		this._stopJobPreventEnabled = stopJobPreventEnabled;
		this._deleteJobPreventEnabled = deleteJobPreventEnabled;
		this._noRequirementsPreventEnabled = noRequirementsPreventEnabled;
		this._noFileUploadsPreventEnabled = noFileUploadsPreventEnabled;
		this._startSessionPreventEnabled = startSessionPreventEnabled;
		this._notificationsEnabled = notificationsEnabled;
		this._snapToInventoryEnabled = snapToInventoryEnabled;
		this._showMonitoringEnabled = showMonitoringEnabled;
		this._showDownloadAllButtonEnabled = showDownloadAllButtonEnabled;
		this._autoAddOnsEnabled = autoAddOnsEnabled;
		this._egressTotal = egressTotal;
		this._egressLimit = egressLimit;
		this._egressMax = egressMax;
		this._egressBuckets = egressBuckets;
		this._storageBuckets = storageBuckets;
		this._serviceFee = serviceFee;
		this._trialStart = trialStart;
		this._credit = credit;

		this._appTracker = appTracker;
		this._fileTracker = fileTracker;
		this._fileChecker = fileChecker;
        this._machines = machines;

		setTimeout(() => this.getUserInformation(), 10000);
    }
    
    get unsignedAgreement(): boolean {
		return this._unsignedAgreement;
    }
    
    set unsignedAgreement(unsignedAgreement: boolean) {
		if (unsignedAgreement === this._unsignedAgreement) {
			return;
		}
		this._unsignedAgreement = unsignedAgreement;
	}

	get name(): string {
		return this._name;
	}

	set name(name: string) {
		if (name === this._name) {
			return;
		}
		this._name = name;
	}

	get phoneNumber(): string {
		return this._phoneNumber;
	}

	set phoneNumber(phoneNumber: string) {
		if (phoneNumber === this._phoneNumber) {
			return;
		}
		this.setUserInformation("phoneNumber", phoneNumber);
		this._phoneNumber = phoneNumber;
	}

	get deploySubMenu(): Page {
		return this._deploySubMenu;
	}

	set deploySubMenu(deploySubMenu: Page) {
		if (deploySubMenu === this._deploySubMenu) {
			return;
		}
		this._deploySubMenu = deploySubMenu;
		if (Global.shouldLogOnEmit) console.log('SignalEmit (' + new Date().getSeconds() + ')');
		this._deploySubMenuChanged.emit(this);
	}

	get intent(): number {
		return this._intent;
	}

	set intent(intent: number) {
		if (intent === this._intent) {
			return;
		}
		this._intent = intent;
		this.setUserInformation("intent", intent.toString());
	}

	get userBudget(): number {
		return this._userBudget;
	}

	set userBudget(userBudget: number) {
		if (userBudget === this._userBudget) {
			return;
		}
		this._userBudget = userBudget;
		this.setUserInformation("userBudget", userBudget.toString());
    }
    
    get maxBudget(): number {
		return this._maxBudget;
	}

	set maxBudget(maxBudget: number) {
		if (maxBudget === this._maxBudget) {
			return;
		}
		this._maxBudget = maxBudget;
		this.setUserInformation("maxBudget", maxBudget.toString());
    }
    
    get budgetCap(): number {
		return this._budgetCap;
	}
    
    get userRate(): number {
		return this._userRate;
	}

	set userRate(userRate: number) {
		if (userRate === this._userRate) {
			return;
		}
		this._userRate = userRate;
		this.setUserInformation("userRate", userRate.toString());
    }
    
    get maxRate(): number {
		return this._maxRate;
	}

	set maxRate(maxRate: number) {
		if (maxRate === this._maxRate) {
			return;
		}
		this._maxRate = maxRate;
		this.setUserInformation("maxRate", maxRate.toString());
    }
    
    get rateCap(): number {
		return this._rateCap;
	}
    
    get userAggregateRate(): number {
		return this._userAggregateRate;
	}

	set userAggregateRate(userAggregateRate: number) {
		if (userAggregateRate === this._userAggregateRate) {
			return;
		}
		this._userAggregateRate = userAggregateRate;
		this.setUserInformation("userAggregateRate", userAggregateRate.toString());
    }
    
    get maxAggregateRate(): number {
		return this._maxAggregateRate;
	}

	set maxAggregateRate(maxAggregateRate: number) {
		if (maxAggregateRate === this._maxAggregateRate) {
			return;
		}
		this._maxAggregateRate = maxAggregateRate;
		this.setUserInformation("maxAggregateRate", maxAggregateRate.toString());
    }
    
    get aggregateRateCap(): number {
		return this._aggregateRateCap;
    }
    
    get userHoldoverTime(): number {
		return this._userHoldoverTime;
	}

	set userHoldoverTime(userHoldoverTime: number) {
		if (userHoldoverTime === this._userHoldoverTime) {
			return;
		}
		this._userHoldoverTime = userHoldoverTime;
		this.setUserInformation("userHoldoverTime", userHoldoverTime.toString());
    }
    
    get maxHoldoverTime(): number {
		return this._maxHoldoverTime;
	}

	set maxHoldoverTime(maxHoldoverTime: number) {
		if (maxHoldoverTime === this._maxHoldoverTime) {
			return;
		}
		this._maxHoldoverTime = maxHoldoverTime;
		this.setUserInformation("maxHoldoverTime", maxHoldoverTime.toString());
    }
    
    get holdoverTimeCap(): number {
		return this._holdoverTimeCap;
	}
    get userRecommendations(): number {
		return this._userRecommendations;
	}

	set userRecommendations(userRecommendations: number) {
		if (userRecommendations === this._userRecommendations) {
			return;
		}
		this._userRecommendations = userRecommendations;
		this.setUserInformation("userRecommendations", userRecommendations.toString());
    }
    
    get maxRecommendations(): number {
		return this._maxRecommendations;
	}

	set maxRecommendations(maxRecommendations: number) {
		if (maxRecommendations === this._maxRecommendations) {
			return;
		}
		this._maxRecommendations = maxRecommendations;
		this.setUserInformation("maxRecommendations", maxRecommendations.toString());
    }
    
    get recommendationsCap(): number {
		return this._recommendationsCap;
	}
    get maxJobs(): number {
		return this._maxJobs;
	}

	set maxJobs(maxJobs: number) {
		if (maxJobs === this._maxJobs) {
			return;
		}
		this._maxJobs = maxJobs;
		this.setUserInformation("maxJobs", maxJobs.toString());
    }

    get jobsCap(): number {
		return this._jobsCap;
	}

    get maxMachines(): number {
		return this._maxMachines;
	}

	set maxMachines(maxMachines: number) {
		if (maxMachines === this._maxMachines) {
			return;
		}
		this._maxMachines = maxMachines;
		this.setUserInformation("maxMachines", maxMachines.toString());
    }
    
    get machinesCap(): number {
		return this._machinesCap;
	}

	get userExpertise(): number {
		return this._userExpertise;
	}

	get billingType(): BillingType {
		return this._billingType;
	}

	get subscriptionActive(): boolean {
		return this._subscriptionActive;
	}

	get lastBillPaid(): boolean {
		return this._lastBillPaid;
	}

	get billingCycleAnchor(): Date {
		return this._billingCycleAnchor;
	}

	get compressFilesEnabled(): boolean {
		return this._compressFilesEnabled;
	}

	set compressFilesEnabled(compressFilesEnabled: boolean) {
		if (compressFilesEnabled === this._compressFilesEnabled) {
			return;
		}
		this._compressFilesEnabled = compressFilesEnabled;
		this.setUserInformation("compressFilesEnabled", compressFilesEnabled.toString());
	}
	
	get lastPage(): number {
		return this._lastPage;
	}

	set lastPage(lastPage: number) {
		if (lastPage === this.lastPage) {
			return;
		}
		this._lastPage = lastPage;
		this.setUserInformation("lastPage", lastPage.toString());
	}
	
	get stopJobPreventEnabled(): boolean {
		return this._stopJobPreventEnabled;
	}

	set stopJobPreventEnabled(stopJobPreventEnabled: boolean) {
		if (stopJobPreventEnabled === this._stopJobPreventEnabled) {
			return;
		}
		this._stopJobPreventEnabled = stopJobPreventEnabled;
		this.setUserInformation("stopJobPreventEnabled", stopJobPreventEnabled.toString());
	}

	get deleteJobPreventEnabled(): boolean {
		return this._deleteJobPreventEnabled;
	}

	set deleteJobPreventEnabled(deleteJobPreventEnabled: boolean) {
		if (deleteJobPreventEnabled === this._deleteJobPreventEnabled) {
			return;
		}
		this._deleteJobPreventEnabled = deleteJobPreventEnabled;
		this.setUserInformation("deleteJobPreventEnabled", deleteJobPreventEnabled.toString());
	}

	get noRequirementsPreventEnabled(): boolean {
		return this._noRequirementsPreventEnabled;
	}

	set noRequirementsPreventEnabled(noRequirementsPreventEnabled: boolean) {
		if (noRequirementsPreventEnabled === this._noRequirementsPreventEnabled) {
			return;
		}
		this._noRequirementsPreventEnabled = noRequirementsPreventEnabled;
		this.setUserInformation("noRequirementsPreventEnabled", noRequirementsPreventEnabled.toString());
	}

	get noFileUploadsPreventEnabled(): boolean {
		return this._noFileUploadsPreventEnabled;
	}

	set noFileUploadsPreventEnabled(noFileUploadsPreventEnabled: boolean) {
		if (noFileUploadsPreventEnabled === this._noFileUploadsPreventEnabled) {
			return;
		}
		this._noFileUploadsPreventEnabled = noFileUploadsPreventEnabled;
		this.setUserInformation("noFileUploadsPreventEnabled", noFileUploadsPreventEnabled.toString());
	}
	
	get startSessionPreventEnabled(): boolean {
		return this._startSessionPreventEnabled;
	}

	set startSessionPreventEnabled(startSessionPreventEnabled: boolean) {
		if (startSessionPreventEnabled === this._startSessionPreventEnabled) {
			return;
		}
		this._startSessionPreventEnabled = startSessionPreventEnabled;
		this.setUserInformation("startSessionPreventEnabled", startSessionPreventEnabled.toString());
	}

	get notificationsEnabled(): boolean {
		return this._notificationsEnabled;
	}

	set notificationsEnabled(notificationsEnabled: boolean) {
		if (notificationsEnabled === this._notificationsEnabled) {
			return;
		}
		this._notificationsEnabled = notificationsEnabled;
		this.setUserInformation("notificationsEnabled", notificationsEnabled.toString());
	}

	get snapToInventoryEnabled(): boolean {
		return this._snapToInventoryEnabled;
	}

	set snapToInventoryEnabled(snapToInventoryEnabled: boolean) {
		if (snapToInventoryEnabled === this._snapToInventoryEnabled) {
			return;
		}
		this._snapToInventoryEnabled = snapToInventoryEnabled;
		this.setUserInformation("snapToInventoryEnabled", snapToInventoryEnabled.toString());
	}

	get showMonitoringEnabled(): boolean {
		return this._showMonitoringEnabled;
	}

	get autoAddOnsEnabled(): boolean {
		return this._autoAddOnsEnabled;
	}

	set autoAddOnsEnabled(autoAddOnsEnabled: boolean) {
		if (autoAddOnsEnabled === this._autoAddOnsEnabled) {
			return;
		}
		this._autoAddOnsEnabled = autoAddOnsEnabled;
		this.setUserInformation("autoAddOnsEnabled", autoAddOnsEnabled.toString());
	}

	get showDownloadAllButtonEnabled(): boolean {
		return this._showDownloadAllButtonEnabled;
	}

	get egressTotal(): number {
		return this._egressTotal;
	}

	get egressLimit(): number {
		return this._egressLimit;
	}

	get egressMax(): number {
		return this._egressMax;
	}

	get egressBuckets(): EgressBucket[] {
		return this._egressBuckets;
	}

	get storageBuckets(): StorageBucket[] {
		return this._storageBuckets;
	}

	get serviceFee(): number {
		return this._serviceFee;
	}

	get trialStart(): Date {
		return this._trialStart;
	}

	set trialStart(trialStart: Date) {
		if (trialStart === this._trialStart) {
			return;
		}
		this._trialStart = trialStart;
		this.setUserInformation("trialStart", trialStart.toISOString());
	}

	get credit(): number {
		return this._credit;
	}

	get fileTracker(): FileTracker {
		return this._fileTracker;
	}

	get appTracker(): AppTracker {
		return this._appTracker;
	}

	get fileChecker(): FileChecker {
		return this._fileChecker;
	}

	set machines(machines: Machines) {
		if (machines === this._machines) {
			return;
		}
		this._machines = machines;
	}

	get machines(): Machines {
		return this._machines;
	}

	public synchronize(responseData: any) {
		// Add apps from user information if they don't already exist
		if (responseData.jobs) {
			NEW_APPS:
			for (let newApp of responseData.jobs) {
				// Ignore this app if we already have an object for it
				for (let app of this.appTracker.finishedSessions) {
					if (app.uuid == newApp.uuid) continue NEW_APPS;
				}
				for (let app of this.appTracker.finishedJobs) {
					if (app.uuid == newApp.uuid) continue NEW_APPS;
				}
				for (let app of this.appTracker.activeSessions) {
					if (app.uuid == newApp.uuid) continue NEW_APPS;
				}
				for (let app of this.appTracker.activeJobs) {
					if (app.uuid == newApp.uuid) continue NEW_APPS;
				}
				this.appTracker.addApp(App.reconstruct(newApp));
			}
		}
	}

	private getUserInformation() {
		if (Global.user == null) return

		const settings = ServerConnection.makeSettings();
		const url = settings.baseUrl + "optumi/get-user-information";
		const init = {
			method: 'POST',
			body: JSON.stringify({
				includeAll: false,
			})
		};
		ServerConnection.makeRequest(
			url,
			init, 
			settings
		).then((response: Response) => {
			Global.handleResponse(response);
			return response.json();
		}).then((body: any) => {
			if (body) {
				if (body.name) this._name = body.name
				if (body.phoneNumber) this._phoneNumber = body.phoneNumber
				if (body.intent) this._intent = +body.intent
				if (body.userBudget) this._userBudget = +body.userBudget
				if (body.maxBudget) this._maxBudget = +body.maxBudget
				if (body.budgetCap) this._budgetCap = +body.budgetCap
				if (body.userRate) this._userRate = +body.userRate
				if (body.maxRate) this._maxRate = +body.maxRate
				if (body.rateCap) this._rateCap = +body.rateCap
				if (body.userAggregateRate) this._userAggregateRate = +body.userAggregateRate
				if (body.maxAggregateRate) this._maxAggregateRate = +body.maxAggregateRate
				if (body.aggregateRateCap) this._aggregateRateCap = +body.aggregateRateCap
				if (body.userHoldoverTime) this._userHoldoverTime = +body.userHoldoverTime
				if (body.maxHoldoverTime) this._maxHoldoverTime = +body.maxHoldoverTime
				if (body.holdoverTimeCap) this._holdoverTimeCap = +body.holdoverTimeCap
				if (body.userRecommendations) this._userRecommendations = +body.userRecommendations
				if (body.maxRecommendations) this._maxRecommendations = +body.maxRecommendations
				if (body.recommendationsCap) this._recommendationsCap = +body.recommendationsCap
				if (body.maxJobs) this._maxJobs = +body.maxJobs
				if (body.jobsCap) this._jobsCap = +body.jobsCap
				if (body.maxMachines) this._maxMachines = +body.maxMachines
				if (body.machinesCap) this._machinesCap = +body.machinesCap
				if (body.userExpertise) this._userExpertise = +body.userExpertise
				if (body.billingType) this._billingType = body.billingType as BillingType
				if (body.subscriptionActive) this._subscriptionActive = body.subscriptionActive
				if (body.lastBillPaid) this._lastBillPaid = body.lastBillPaid
				if (body.billingCycleAnchor) this._billingCycleAnchor = new Date(body.billingCycleAnchor)
				if (body.compressFilesEnabled) this._compressFilesEnabled = body.compressFilesEnabled
				if (body.lastPage) this._lastPage = body.lastPage
				if (body.stopJobPreventEnabled) this._stopJobPreventEnabled = body.stopJobPreventEnabled
				if (body.deleteJobPreventEnabled) this._deleteJobPreventEnabled = body.deleteJobPreventEnabled
				if (body.noRequirementsPreventEnabled) this._noRequirementsPreventEnabled = body.noRequirementsPreventEnabled
				if (body.noFileUploadsPreventEnabled) this._noFileUploadsPreventEnabled = body.noFileUploadsPreventEnabled
				if (body.startSessionPreventEnabled) this._startSessionPreventEnabled = body.startSessionPreventEnabled
				if (body.notificationsEnabled) this._notificationsEnabled = body.notificationsEnabled
				if (body.snapToInventoryEnabled) this._snapToInventoryEnabled = body.snapToInventoryEnabled
				if (body.showMonitoringEnabled) this._showMonitoringEnabled = body.showMonitoringEnabled
				if (body.showDownloadAllButtonEnabled) this._showDownloadAllButtonEnabled = body.showDownloadAllButtonEnabled
				if (body.autoAddOnsEnabled) this._autoAddOnsEnabled = body.autoAddOnsEnabled
				if (body.egressTotal) this._egressTotal = +body.egressTotal
				if (body.egressLimit) this._egressLimit = +body.egressLimit
				if (body.egressMax) this._egressMax = +body.egressMax
				if (body.egressBuckets) {
					var egressBuckets = []
					for (var i = 0; i < body.egressBuckets.length; i++) {
						egressBuckets.push({ limit: body.egressBuckets[i].limit.val, cost: body.egressBuckets[i].cost } as EgressBucket)
					}
					this._egressBuckets = egressBuckets
				}
				if (body.storageBuckets) {
					var storageBuckets = []
					for (var i = 0; i < body.storageBuckets.length; i++) {
						storageBuckets.push({ limit: body.storageBuckets[i].limit.val, cost: body.storageBuckets[i].cost } as EgressBucket)
					}
					this._storageBuckets = storageBuckets
				}
				if (body.egressMax) this._egressMax = +body.egressMax
				if (body.serviceFee) this._serviceFee = +body.serviceFee
				if (body.trialStart) this._trialStart = new Date(body.trialStart)
				if (body.credit) this._credit = +body.credit
				this._userInformationChanged.emit(this);

				// if (this._egressTotal >= this._egressLimit) {
					// const action = (key: SnackbarKey) => (
					// 	<>
					// 		<SubscribeButton variant='outlined' color='secondary'/>
					// 		<IconButton
					// 			onClick={() => { Global.snackbarClose.emit(key) }}
					// 			sx={{padding: '3px'}}
					// 		>
					// 			<Close sx={{ color: 'white' }}/>
					// 		</IconButton>
					// 	</>
					// );
					// Global.snackbarEnqueue.emit(new Snackbar(
					// 	'You have hit the ' + FormatUtils.styleCapacityUnitValue()(this._egressLimit) + ' egress limit',
					// 	{ variant: 'error', persist: true, key: new Date().toISOString(), action }
					// ));
				// }
			}
			setTimeout(() => this.getUserInformation(), 10000);
		}, () => {
			// Make sure we still poll even if we encounter an error
			setTimeout(() => this.getUserInformation(), 10000);
		});
	}

	private setUserInformation(param: string, value: string) {
		const settings = ServerConnection.makeSettings();
		const url = settings.baseUrl + "optumi/set-user-information";
		const init = {
			method: 'POST',
			body: JSON.stringify({
				'param': param,
				'value': value,
			})
		};
		ServerConnection.makeRequest(
			url,
			init, 
			settings
		).then((response: Response) => {
			Global.handleResponse(response);
		});
		this._userInformationChanged.emit(this);
	}

	public changePassword(loginName: string, oldPassword: string, newPassword: string) {
		const settings = ServerConnection.makeSettings();
		const url = settings.baseUrl + "optumi/change-password";
		const init = {
			method: 'POST',
			body: JSON.stringify({
				'loginName': loginName,
				'oldPassword': oldPassword,
				'newPassword': newPassword,
			})
		};
		return ServerConnection.makeRequest(
			url,
			init, 
			settings
		).then((response: Response) => {
			Global.handleResponse(response);
		});	
	}
}
