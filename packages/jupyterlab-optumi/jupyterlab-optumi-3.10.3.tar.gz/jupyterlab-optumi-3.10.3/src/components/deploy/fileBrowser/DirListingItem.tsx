/*
**  Copyright (C) Optumi Inc - All rights reserved.
**
**  You may only use this code under license with Optumi Inc and any distribution or modification is strictly prohibited.
**  To receive a copy of the licensing terms please write to contact@optumi.com or visit us at http://www.optumi.com.
**/

import * as React from 'react'
import { Global, SPAN } from '../../../Global';

import DirListingItemIcon from './DirListingItemIcon'
import { FilterableFile } from './DirListingContent';

import moment from 'moment'
import { StringExt } from '@lumino/algorithm';

interface IProps {
    file: FilterableFile
    filter: string
    selected: boolean
    onClick: (event: React.MouseEvent<HTMLLIElement, MouseEvent>) => void
    onDoubleClick: (event: React.MouseEvent<HTMLLIElement, MouseEvent>) => void
}

interface IState {}

export default class DirListingItem extends React.Component<IProps, IState> {

    constructor(props: IProps) {
        super(props)
        this.state = {
            focused: false
        }
    }

    private formatSize = (size: number): string => {
        if (size < Math.pow(1000, 1)) return (size / Math.pow(1000, 0)).toFixed(1) + ' Bytes';
        if (size < Math.pow(1000, 2)) return (size / Math.pow(1000, 1)).toFixed(1) + ' KB';
        if (size < Math.pow(1000, 3)) return (size / Math.pow(1000, 2)).toFixed(1) + ' MB';
        if (size < Math.pow(1000, 4)) return (size / Math.pow(1000, 3)).toFixed(1) + ' GB';
        return (size / Math.pow(1000, 4)).toFixed(1) + ' TB';
    }

    public render = (): JSX.Element => {
		if (Global.shouldLogOnRender) console.log('ComponentRender (' + new Date().getSeconds() + ')');
        const file = this.props.file.file
        const path = file.path.replace(file.name, '').replace(/\/$/, '')
        const html = StringExt.highlight(file.name, this.props.file.indices, (s: string) => '<mark style="padding: 0px;">' + s + '</mark>').join('');
        return (
            <li
                className={'jp-DirListing-item' + (this.props.selected ? ' jp-mod-selected' : '')}
                onClick={(event: React.MouseEvent<HTMLLIElement, MouseEvent>) => this.props.onClick(event)}
                onDoubleClick={(event: React.MouseEvent<HTMLLIElement, MouseEvent>) => this.props.onDoubleClick(event)}
                title={
`Name: ${file.name}
${file.size === null ? '' : `Size: ${this.formatSize(file.size)}
`}${path === '' ? '' : `Path: ${path}
`}Created: ${moment(file.created).format('YYYY-MM-DD hh:mm:ss')}
Modified: ${moment(file.last_modified).format('YYYY-MM-DD hh:mm:ss')}
Writable: ${file.writable}`}
            >
                <DirListingItemIcon fileType={file.type} mimetype={file.mimetype} />
                <SPAN className='jp-DirListing-itemText' dangerouslySetInnerHTML={{ __html: html }}/>
                <SPAN
                    className='jp-DirListing-itemModified'
                    title={moment(file.last_modified).format('MMM D, YYYY h:mm A')}
                >
                    {moment(file.last_modified).fromNow()}
                </SPAN>
            </li>
        )
    }
}
