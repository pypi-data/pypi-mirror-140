/*
**  Copyright (C) Optumi Inc - All rights reserved.
**
**  You may only use this code under license with Optumi Inc and any distribution or modification is strictly prohibited.
**  To receive a copy of the licensing terms please write to contact@optumi.com or visit us at http://www.optumi.com.
**/

import * as React from 'react'
import { DIV, Global } from '../../Global';

import { AnnotationInput } from '../../components/deploy/AnnotationInput';
import ExtraInfo from '../../utils/ExtraInfo';
import { App } from './App';
import { LightweightApp } from './LightweightApp'

interface IProps {
    app: App | LightweightApp;
}

interface IState {}

export class IdentityAppComponent extends React.Component<IProps, IState> {

    public render = (): JSX.Element => {
        if (Global.shouldLogOnRender) console.log('ComponentRender (' + new Date().getSeconds() + ')');
        const lightweightApp = this.props.app
        return (
				<DIV sx={{paddingLeft: '3px'}}> {/* the padding is 7px because the height it needs to take up is 36 and the height of this 16px font is 22px */}
					<ExtraInfo reminder={lightweightApp.path}>
						<DIV sx={{paddingBottom: '7px', fontSize: 'var(--jp-ui-font-size1)', lineHeight: '1', fontWeight: 'normal', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}}>
							{lightweightApp.name}
						</DIV>
					</ExtraInfo>
					<AnnotationInput
						getValue={() => lightweightApp.config.annotation}
						saveValue={(value: string) => {
							const config = lightweightApp.config.copy();
							config.annotation = value;
							lightweightApp.config = config;
						}}
						placeholder={lightweightApp.runNum == 0 ? 'Add annotation' : 'Run #' + lightweightApp.runNum}
					/>
					{/* <SPAN sx={{fontSize: '13px', lineHeight: '1', fontWeight: 'normal', color: 'gray'}}>
						{this._config.annotation}
					</SPAN> */}
				</DIV>
        )
    }
}
