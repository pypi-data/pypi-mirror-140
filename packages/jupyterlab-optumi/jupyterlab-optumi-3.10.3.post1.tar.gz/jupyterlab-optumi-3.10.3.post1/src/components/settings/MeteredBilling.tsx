/*
**  Copyright (C) Optumi Inc - All rights reserved.
**
**  You may only use this code under license with Optumi Inc and any distribution or modification is strictly prohibited.
**  To receive a copy of the licensing terms please write to contact@optumi.com or visit us at http://www.optumi.com.
**/

import * as React from 'react';
import { DIV, Global } from '../../Global';

import { Button, Chip, CircularProgress, Divider, LinearProgress } from '@mui/material';

import { ServerConnection } from '@jupyterlab/services';

import { GetApp as GetAppIcon } from '@mui/icons-material';
import FormatUtils from '../../utils/FormatUtils';
import { Header, Label, Switch } from '../../core';
import { InfoPopup } from '../../core/InfoPoppup';
import { EgressBuckets } from '../EgressBuckets';
import { StorageBuckets } from '../StorageBuckets';
import WarningPopup from '../../core/WarningPopup';
import { PlansPopup } from '../../core/PlansPopup';


// Properties from parent
interface IProps {
    machineCost: number
    serviceFeeCost: number
    storageCost: number
    egressCost: number
}

// Properties for this component
interface IState {
    portalWaiting: boolean,
    showStoragePopup: boolean
    plansOpen: boolean
}

export class MeteredBilling extends React.Component<IProps, IState> {
    _isMounted = false;

    constructor(props: IProps) {
        super(props);
        this.state = {
            portalWaiting: false,
            showStoragePopup: false,
            plansOpen: false,
        }
    }

    private formatCost = (cost: number): string => {
        var ret = '$' + cost.toFixed(2)
        if (ret == '$0.00') return '--'
        return ret
    }

    private ordinalSuffixOf = (i: number) => {
        var j = i % 10,
            k = i % 100;
        if (j == 1 && k != 11) {
            return i + "st";
        }
        if (j == 2 && k != 12) {
            return i + "nd";
        }
        if (j == 3 && k != 13) {
            return i + "rd";
        }
        return i + "th";
    }

    private handlePortalClick = async () => {
        this.safeSetState({ portalWaiting: true });
        
        const settings = ServerConnection.makeSettings();
        const url = settings.baseUrl + "optumi/create-portal";
        const init: RequestInit = {
            method: 'POST',
            body: JSON.stringify({
                redirect: settings.baseUrl,
            }),
        };
        ServerConnection.makeRequest(
            url,
            init,
            settings
        ).then((response: Response) => {
            Global.handleResponse(response);
            return response.json();
        }).then((body: any) => {
            // When the customer clicks on the button, redirect them to the portal
            window.location.href = body.url;
            this.safeSetState({ portalWaiting: false });
        });
    };

    private getDuration = (record: any): string => {
        var endTime = new Date(record.endTime as string);
        var startTime = new Date(record.startTime as string);
        var diff = endTime.getTime() - startTime.getTime();
        var time = FormatUtils.msToTime(diff).split(':');
        var formatted;
        if (time.length == 3) {
            formatted = time[0] + 'h ' + time[1] + 'm ' + time[2] + 's';
        } else {
            formatted = time[0] + 'm ' + time[1] + 's';
        }
        return formatted;
    }

    private saveDetailedBilling = () => {
        if (Global.user == null) return;
        const settings = ServerConnection.makeSettings();
        const url = settings.baseUrl + "optumi/get-detailed-billing";
        const now = new Date();
        const threeMonthsAgo = new Date();
        threeMonthsAgo.setMonth(threeMonthsAgo.getMonth()-3);
		const init: RequestInit = {
			method: 'POST',
            body: JSON.stringify({
				startTime: threeMonthsAgo.toISOString(),
				endTime: now.toISOString(),
			}),
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
                const data: string[][] = [];

                for (let record of body.records) {
                    switch (record.type) {
                        case 'Machine':
                            const machine = body.machines[record.provider + ':' + record.product];
                            data.push(
                                [
                                    "Machine",
                                    new Date(record.startTime).toLocaleString().replace(/,/g, ''),
                                    new Date(record.endTime).toLocaleString().replace(/,/g, ''),
                                    this.getDuration(record),
                                    '$' + (record.rate * 3600),
                                    '$' + record.cost,
                                    machine.graphicsNumCards > 0 ? (machine.graphicsNumCards + 'x' + machine.graphicsCardType) : 'No GPU',
                                    machine.computeCores[1] + ' cores',
                                    FormatUtils.styleCapacityUnitValue()(machine.memorySize),
                                    FormatUtils.styleCapacityUnitValue()(machine.storageSize)
                                ]
                            );
                            break;
                        case 'Payment':
                            data.push(
                                [
                                    "Payment",
                                    new Date(record.time).toLocaleString().replace(/,/g, ''),
                                    '',
                                    '',
                                    '',
                                    '$' + record.cost,
                                    '',
                                    '',
                                    '',
                                    ''
                                ]
                            );
                            break;
                        case 'Egress':
                            data.push(
                                [
                                    "Egress",
                                    new Date(record.time).toLocaleString().replace(/,/g, ''),
                                    '',
                                    '',
                                    '',
                                    '$' + record.cost,
                                    '',
                                    '',
                                    '',
                                    ''
                                ]
                            );
                            break;
                        case 'Storage':
                            data.push(
                                [
                                    "Storage",
                                    new Date(record.time).toLocaleString().replace(/,/g, ''),
                                    '',
                                    '',
                                    '',
                                    '$' + record.cost,
                                    '',
                                    '',
                                    '',
                                    ''
                                ]
                            );
                            break;
                        case 'Service Fee':
                            data.push(
                                [
                                    "Service Fee",
                                    new Date(record.startTime).toLocaleString().replace(/,/g, ''),
                                    new Date(record.endTime).toLocaleString().replace(/,/g, ''),
                                    this.getDuration(record),
                                    '$' + (record.rate * 3600),
                                    '$' + record.cost,
                                    '',
                                    '',
                                    '',
                                    ''
                                ]
                            );
                            break;
                        default:
                            console.error("Unknown billing record type " + record.type);
                    } 
                }

                var sorted: string[][] = data.sort((n1: string[], n2: string[]) => {
                    if (new Date(n1[1]) > new Date(n2[1])) {
                        return 1;
                    }
                    if (new Date(n1[1]) < new Date(n2[1])) {
                        return -1;
                    }
                    return 0;
                });

                const headers = [
                    ["Type", "Start Time", "End Time", "Duration", "Rate ($/hr)", "Cost ($)", "GPU", "CPU", "RAM", "Disk"]
                ];
                
                var link = document.createElement("a");
                var blob = new Blob([headers.map(e => e.join(",")).join("\n") + '\n' + sorted.map(e => e.join(",")).join("\n") + '\n'], {
                    type: "data:text/csv;charset=utf-8,"
                });
                link.setAttribute("href", window.URL.createObjectURL(blob));
                link.setAttribute("download", "billing_records.csv");
                document.body.appendChild(link); // Required for FF
                link.click();
            }
        });
    }

    private getCostDiv = (costType: string = '') => {
        return (
            <DIV
                sx={{display: 'inline-flex', width: '100%', padding: '3px 0px'}}
            >
                <DIV sx={{
                    height: '12px',
                    margin: '0px 12px',
                    lineHeight: '12px',
                    textAlign: 'left',
                    whiteSpace: 'pre',
                }}>
                    {costType == 'Service Fee' ? (
                        'Optumi service'
                    ) : costType == 'Machine' ? (
                        'Machines'
                    ) : costType == 'Storage' ? (
                        'Storage'
                    ) : costType == 'Egress' ? (
                        'Egress'
                    ) : (
                        'Total cost'
                    )}
                </DIV>
                <DIV sx={{
                    width: '100%',
                    height: '12px',
                    margin: '0px 6px',
                    lineHeight: '12px',
                    textAlign: 'right',
                    display: 'flex',
                    justifyContent: 'end',
                }}>
                    {costType == 'Service Fee' ? (
                        <DIV sx={{padding: '0px 6px', fontSize: '12px'}}>
                            {this.props.serviceFeeCost == null ? (<LinearProgress sx={{width: '25px'}}/>) : this.formatCost(this.props.serviceFeeCost)}
                        </DIV>
                    ) : costType == 'Machine' ? (
                        <DIV sx={{padding: '0px 6px', fontSize: '12px'}}>
                            {this.props.machineCost == null ? (<LinearProgress sx={{width: '25px'}}/>) : this.formatCost(this.props.machineCost)}
                        </DIV>
                    ) : costType == 'Storage' ? (
                        <DIV sx={{padding: '0px 6px', fontSize: '12px'}}>
                            {this.props.storageCost == null ? (<LinearProgress sx={{width: '25px'}}/>) : this.formatCost(this.props.storageCost)}
                        </DIV>
                    ) : costType == 'Egress' ? (
                        <DIV sx={{padding: '0px 6px', fontSize: '12px'}}>
                            {this.props.egressCost == null ? (<LinearProgress sx={{width: '25px'}}/>) : this.formatCost(this.props.egressCost)}
                        </DIV>
                    ) : (
                        <DIV sx={{padding: '0px 6px', fontSize: '12px'}}>
                            {(this.props.egressCost == null || this.props.machineCost == null || this.props.storageCost == null || this.props.serviceFeeCost == null) ? 
                            (<LinearProgress sx={{width: '25px'}}/>) : 
                            (this.formatCost(+(this.props.machineCost.toFixed(2)) + +(this.props.egressCost.toFixed(2)) + +(this.props.storageCost.toFixed(2)) + +(this.props.serviceFeeCost.toFixed(2))))}
                        </DIV>
                    )}
                </DIV>
            </DIV>
        )
    }

	// The contents of the component
	public render = (): JSX.Element => {
		if (Global.shouldLogOnRender) console.log('ComponentRender (' + new Date().getSeconds() + ')');

        const credit = Global.user.credit;

        const now = new Date();
        var nextAnchor = Global.user.billingCycleAnchor;
        if (nextAnchor) {
            nextAnchor.setFullYear(now.getFullYear())
            nextAnchor.setMonth(now.getMonth());
            if (nextAnchor < now) nextAnchor.setMonth(nextAnchor.getMonth()+1);
        } else {
            nextAnchor = new Date(0);
        }

		return (
            <>
                <DIV sx={{display: 'flex'}}>
                    <Header title='Current plan' />
                    <PlansPopup
                        open={this.state.plansOpen}
                        handleClose={() => this.safeSetState({ plansOpen: false })}
                        openButton={
                            <Chip label='View plans' variant='filled'
                                sx={{
                                    height: '20px',
                                    fontSize: '12px',
                                    marginY: 'auto',
                                }}
                                onClick={() => this.safeSetState({ plansOpen: true })}
                            />
                        }
                    />
                </DIV>
                <Label label='Starter'
                    getValue={() => '$0.10/hour'}
                    align='left' valueAlign='right' lineHeight='20px'
                />
                <Label label='Storage'
                    getValue={() => (Global.user.fileTracker.limit == Global.user.storageBuckets[0].limit ? 'Free up to ' : 'Up to ') + FormatUtils.styleCapacityUnitValue()(Global.user.fileTracker.limit)}
                    align='left' valueAlign='right' lineHeight='20px'
                />
                <Label label='Egress'
                    getValue={() => (Global.user.egressLimit == Global.user.egressBuckets[0].limit ? 'Free up to ' : 'Up to ') + FormatUtils.styleCapacityUnitValue()(Global.user.egressLimit)}
                    align='left' valueAlign='right' lineHeight='20px'
                />
                <DIV sx={{display: 'flex', width: '100%'}}>
                    <Switch label='Dynamic upgrades'
                        getValue={() => Global.user.autoAddOnsEnabled}
                        saveValue={value => {
                            Global.user.autoAddOnsEnabled = value 
                            if (!value && Global.user.fileTracker.total > Global.user.egressBuckets[0].limit) {
                                this.safeSetState({showStoragePopup: true})
                            }
                        }}
                        labelBefore={true}
                        sx={{width: '100%', paddingY: 0.25, marginRight: '12px'}}
                        info={(
                            <InfoPopup title='Dynamic upgrades' sx={{marginY: 'auto', marginLeft: 0.5, marginRight: -0.5, marginBottom: '2px'}} popup={
                                <DIV sx={{padding: 1}}>
                                    <DIV>
                                        If enabled, storage and egress tiers will be automatically upgraded as you consume more of each resource. For example, if in a given billing period you use {FormatUtils.styleCapacityUnitValue()((Global.user.storageBuckets[1].limit + Global.user.storageBuckets[2].limit) / 2)} of storage, you will be charged ${Global.user.storageBuckets[2].cost}.
                                    </DIV>
                                    <br/>
                                    <DIV>
                                        If disabled, you will not be able to consume more than the storage and egress limits included in your current tier.
                                    </DIV>
                                    <br/>
                                    <DIV>
                                        At the beginning of every billing cycle you will start off in the lowest possible tier based on your usage.
                                    </DIV>
                                    <br/>
                                    <StorageBuckets buckets={Global.user.storageBuckets}/>
                                    <EgressBuckets buckets={Global.user.egressBuckets}/>
                                </DIV>
                            } />
                        )}
                    />
                    <WarningPopup
                        open={this.state.showStoragePopup}
                        headerText="Dynamic storage"
                        bodyText={`If you would like to shift into a lower storage tier for next billing cycle, you will have to delete more data. For example, to shift into the free storage tier your usage must be under ${FormatUtils.styleCapacityUnitValue()(Global.user.storageBuckets[0].limit)}.`}
                        continue={{
                            text: `Ok`,
                            onContinue: (prevent: boolean) => {
                                this.safeSetState({ showStoragePopup: false })
                            },
                            color: `primary`,
                        }}
                    />
                </DIV>
                <Header title={`To be billed on ${nextAnchor.toLocaleString('default', { month: 'long' })} ${this.ordinalSuffixOf(nextAnchor.getDate())}`} />
                {this.getCostDiv('Service Fee')}
                {this.getCostDiv('Machine')}
                {this.getCostDiv('Storage')}
                {this.getCostDiv('Egress')}
                <Divider variant='fullWidth' sx={{margin: '12px'}}/>
                {this.getCostDiv()}
                {credit < 0 && (
                    <DIV sx={{marginX: 1, marginY: 0.75}}>
                        A ${(-credit).toFixed(2)} credit will be applied to your next bill
                    </DIV>
                )}
                <DIV sx={{display: 'flex', padding: 0.5}}>
                    <Button 
                        disabled={this.state.portalWaiting} 
                        variant="contained"
                        color="primary"
                        sx={{width: '50%', margin: 0.5}}
                        onClick={this.handlePortalClick}
                    >
                        {this.state.portalWaiting ? (<CircularProgress size='1.75em'/>) : 'Payment settings'}
                    </Button>
                    <Button
                        fullWidth
                        variant="outlined"
                        color="primary"
                        startIcon={<GetAppIcon />}
                        sx={{width: '50%', margin: 0.5}}
                        onClick={this.saveDetailedBilling}
                    >
                        Billing records
                    </Button>
                </DIV>
            </>
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
