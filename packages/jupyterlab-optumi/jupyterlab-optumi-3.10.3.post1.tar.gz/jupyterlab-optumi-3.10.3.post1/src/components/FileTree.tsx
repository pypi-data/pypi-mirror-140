/*
**  Copyright (C) Optumi Inc - All rights reserved.
**
**  You may only use this code under license with Optumi Inc and any distribution or modification is strictly prohibited.
**  To receive a copy of the licensing terms please write to contact@optumi.com or visit us at http://www.optumi.com.
**/

import * as React from 'react'
import { DIV, Global, SPAN } from '../Global';

import { TreeView, TreeItem } from '@mui/lab'
import { withStyles } from '@mui/styles';
import { ChevronRight, ExpandMore } from '@mui/icons-material';

import FileExtensionIcon from './FileExtensionIcon';
import { FileMetadata } from './deploy/fileBrowser/FileBrowser';
import moment from 'moment';

type TreeNode = DirectoryNode | FileNode

interface DirectoryNode {
    path: string
    file: string
    children: TreeNode[]
    metadata: undefined
}

interface FileNode {
    path: string
    file: string
    metadata: FileMetadata
    children: undefined
}

interface HidableIcon {
    icon: JSX.Element
    width: number
    height: number
}

interface IProps {
    files: FileMetadata[]
    fileHidableIcon?: (file: FileMetadata) => HidableIcon
    directoryHidableIcon?: (path: string) => HidableIcon
    fileTitle?: (file: FileMetadata) => string
    directoryTitle?: (path: string) => string
}

interface IState {
    expanded: string[]
}

export class FileTree extends React.Component<IProps, IState> {

    constructor(props: IProps) {
        super(props);
        
        this.state = {
            expanded: [],
        }
    }

    private renderTreeItems = (files: FileMetadata[]): JSX.Element[] | undefined => {

        const generateTreeStructure = (): TreeNode => {

            const generatePathStructure = (metadata: FileMetadata, path: string, file: string): TreeNode => {
                if (file.startsWith('~/')) file = file.replace('~/', '')
                let parts = file.split(/(?<=^\/?[^\/]+)(?=\/)/)
                if (parts.length > 1) {
                    return {
                        path: path,
                        file: parts[0],
                        children: [generatePathStructure(metadata, path + parts[0], parts[1])]
                    } as DirectoryNode
                } else {
                    return {path, file, metadata} as FileNode
                }
            }

            const mergePathStructure = (treeStructure: TreeNode, pathStructure: TreeNode): TreeNode => {
                if (treeStructure.children === undefined) {
                    treeStructure.children = [pathStructure]
                    return treeStructure
                } else if (pathStructure.children === undefined) {
                    treeStructure.children.push(pathStructure)
                    return treeStructure
                } else {
                    for (let i = 0; i < treeStructure.children.length; i++) {
                        let child = treeStructure.children[i]
                        if (child.file === pathStructure.file) {
                            treeStructure.children[i] = mergePathStructure(child, pathStructure.children[0])
                            return treeStructure
                        }
                    }
                    treeStructure.children.push(pathStructure)
                    return treeStructure
                }
            }

            let treeStructure: TreeNode = {path: '', file: '', children: []} as DirectoryNode
            for (let file of files) {
                let pathStructure = generatePathStructure(file, '', file.path)
                treeStructure = mergePathStructure(treeStructure, pathStructure)
            }
            return treeStructure
        }

        const collapseTreeStructure = (structure: TreeNode): TreeNode => {
            if (structure.children === undefined) {
                return structure                
            } else if (structure.children.length === 1) {
                let child = structure.children[0]
                structure.file += child.file
                structure.metadata = child.metadata
                structure.children = child.children
                return collapseTreeStructure(structure)
            } else {
                for (let i = 0; i < structure.children.length; i++) {
                    structure.children[i] = collapseTreeStructure(structure.children[i])
                }
                return structure
            }
        }

        const renderTreeStructure = (structure: TreeNode, includeSlash: boolean): JSX.Element => {
            let hasChildren = Array.isArray(structure.children)
            let cappedMessage
            const maxChildren = 250
            if (hasChildren && structure.children.length > maxChildren) {
                cappedMessage = (
                    <TreeItem
                        endIcon={<></>}
                        key={structure.path + structure.file + 'toomany'}
                        nodeId={structure.path + structure.file + 'toomany'}
                        label={(
                            <DIV sx={{
                                flexGrow: 1,
                                fontSize: 'var(--jp-ui-font-size1)',
                                fontFamily: 'var(--jp-ui-font-family)',
                                overflowX: 'hidden',
                                whiteSpace: 'nowrap',
                                textOverflow: 'ellipsis',
                            }}>
                                Too many files, hiding remaining {structure.children.length - maxChildren}
                            </DIV>
                        )}
                    />
                )
            }
            return (
                <FileTreeItem
                    structure={structure}
                    includeSlash={includeSlash}
                    title={hasChildren ? (
                        this.props.directoryTitle && this.props.directoryTitle(structure.path + structure.file)
                    ) : (
                        this.props.fileTitle && this.props.fileTitle(structure.metadata)
                    )}
                    hidableIcon={hasChildren ? (
                        this.props.directoryHidableIcon ? this.props.directoryHidableIcon(structure.path + structure.file) : undefined
                    ) : (
                        this.props.fileHidableIcon ? this.props.fileHidableIcon(structure.metadata) : undefined
                    )}
                >
                    {hasChildren ? (
                        <>
                            {structure.children.splice(0, maxChildren).map((child: TreeNode) => renderTreeStructure(child, false))}
                            {cappedMessage}
                        </>
                    ) : undefined}
                </FileTreeItem>
            )
        }

        let structure: TreeNode = generateTreeStructure()
        return Array.isArray(structure.children) ? (
            structure.children.map((child: TreeNode) => renderTreeStructure(collapseTreeStructure(child), true))
        ) : undefined
    }

    public render = (): JSX.Element => {
        if (Global.shouldLogOnRender) console.log('ComponentRender (' + new Date().getSeconds() + ')');
        return (
            <TreeView
                disableSelection
                defaultCollapseIcon={<ExpandMore />}
                defaultExpandIcon={<ChevronRight />}
                expanded={this.state.expanded}
                onNodeToggle={(event: React.ChangeEvent<{}>, nodeIds: string[]) => {
                    this.setState({ expanded: nodeIds })
                }}
            >
                {this.renderTreeItems(this.props.files)}
            </TreeView>
        )
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

interface ItemProps {
    structure: TreeNode
    includeSlash: boolean
    title?: string
    hidableIcon?: HidableIcon
    children?: undefined | JSX.Element | JSX.Element[]
}

interface ItemState {
    hovered: boolean
}

export class FileTreeItem extends React.Component<ItemProps, ItemState> {
    private _isMounted = false
    private StyledTreeItem: any

    constructor(props: ItemProps) {
        super(props)

        this.StyledTreeItem = withStyles({
            '@global': {
                '.hovered > .MuiTreeItem-root > .MuiTreeItem-content': {
                    width: 'calc(100% - ' + (props.hidableIcon ? props.hidableIcon.width : 0) + 'px)',
                    transitionDuration: '300ms',
                }
            },
            root: {
                width: '100%',
                transitionDuration: '300ms',
            },
            label: {
                display: 'flex',
                width: 'calc(100% - 19px)',
                alignItems: 'center',
            }
        })(TreeItem)

        this.state = {
            hovered: false,
        }
    }

    public render = (): JSX.Element => {
        if (Global.shouldLogOnRender) console.log('ComponentRender (' + new Date().getSeconds() + ')');
        const structure = this.props.structure
        const hidableIcon = this.props.hidableIcon
        return (
            <DIV
                key={structure.path + structure.file}
                className={this.state.hovered ? 'hovered' : undefined}
                sx={{display: 'flex', width: '100%', position: 'relative'}}
            >
                {hidableIcon && (
                    <DIV
                        sx={{position: 'absolute', right: '0px'}}
                        onMouseOver={() => this.safeSetState({hovered: true})}
                        onMouseOut={() => this.safeSetState({hovered: false})}
                    >
                        <DIV sx={{display: 'inline-flex', position: 'absolute', right: '0px'}}>
                            {hidableIcon.icon}
                        </DIV>
                        <DIV sx={{
                            position: 'absolute',
                            right: this.state.hovered ? hidableIcon.width + 'px' : '0px',
                            width: this.state.hovered ? '0px' : hidableIcon.width + 'px',
                            height: hidableIcon.height,
                            backgroundColor: 'var(--jp-layout-color1)',
                            transitionDuration: '300ms',
                        }} />
                    </DIV>
                )}
                <this.StyledTreeItem
                    nodeId={structure.path + structure.file}
                    endIcon={<FileExtensionIcon path={structure.file}/>}
                    label={(
                        <DIV
                            onMouseOver={() => this.safeSetState({hovered: true})}
                            onMouseOut={() => this.safeSetState({hovered: false})}
                            title={this.props.title}
                            sx={{
                                flexGrow: 1,
                                fontSize: 'var(--jp-ui-font-size1)',
                                fontFamily: 'var(--jp-ui-font-family)',
                                overflowX: 'hidden',
                                whiteSpace: 'nowrap',
                                textOverflow: 'ellipsis',
                                height: hidableIcon && hidableIcon.height + 'px',
                                lineHeight: hidableIcon && hidableIcon.height + 'px',
                            }}
                        >
                            {structure.file.replace(this.props.includeSlash ? '' : /^\//, '') /*+ (hasChildren ? '/' : '')*/}
                            {structure.metadata && (<SPAN sx={{marginLeft: '6px', opacity: '0.5'}}>{moment(structure.metadata.last_modified).format('YYYY-MM-DD hh:mm:ss')}</SPAN>)}
                        </DIV>
                    )}
                >
                    {this.props.children}
                </this.StyledTreeItem>
            </DIV>
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

    public shouldComponentUpdate = (nextProps: ItemProps, nextState: ItemState): boolean => {
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
