/*
**  Copyright (C) Optumi Inc - All rights reserved.
**
**  You may only use this code under license with Optumi Inc and any distribution or modification is strictly prohibited.
**  To receive a copy of the licensing terms please write to contact@optumi.com or visit us at http://www.optumi.com.
**/

import { Global } from "../Global";

import { ComputeConfig } from "./ComputeConfig";
import { GraphicsConfig } from "./GraphicsConfig";
import { MemoryConfig } from "./MemoryConfig";
import { NotificationConfig } from "./NotificationConfig";
import { PackageConfig } from "./PackageConfig";
import { StorageConfig } from "./StorageConfig";
import { UploadConfig } from "./UploadConfig";
import { User } from "./User";

export enum Expertise {
	BASIC = "basic",
    RATING = "rating",
    SIMPLIFIED = "simplified",
	COMPONENT = "component",
	EQUIPMENT = "equipment"
}

export class OptumiConfig {
	public intent: number;
	public compute: ComputeConfig;
	public graphics: GraphicsConfig;
    public memory: MemoryConfig;
    public storage: StorageConfig;
	public upload: UploadConfig;
	public machineAssortment: string[];
	public notifications: NotificationConfig;
	public package: PackageConfig;
	public interactive: boolean;
	public annotation: string;
	
	constructor(map: any = {}, version: string = Global.version, user: User = null) {
		switch (version) {
			case "0.3.0":
			case "0.3.1":
			case "0.3.2":
			case "0.3.3":
			case "0.3.4":
			case "0.3.5":
			case "0.3.6":
			case "0.3.7":
			case "0.3.8":
			case "0.3.9":
			case "0.3.10":
			case "0.3.11":
			case "0.3.12":
			case "0.3.13":
            case "0.3.14":
            case "0.3.15":
            case "0.3.16":
            case "0.3.17":
            case "20.9.0-0":
            case "20.9.1-0":
            case "20.9.1-1":
            case "20.10.0-0":
            case "20.10.1":
            case "20.10.1-1":
            case "20.10.1-2":
            case "20.10.1-3":
            case "20.10.1-4":
            case "20.10.1-5":
				/// Anything before this will result in default metadata
				map = {}
			case "20.12.0":
			case "20.12.0-1":
			case "2.1.0":
			case "2.1.1":
			case "2.1.2":
			case "2.2.0":
			case "3.3.0":
			case "3.3.1":
			case "3.3.2":
			case "3.5.0":
			case "3.5.1":
			case "3.6.0":
			case "3.7.0":
			case "3.7.1":
			case "3.7.2":
			case "3.7.3":
			case "3.8.0":
			case "3.8.1":
			case "3.8.2":
			case "3.8.3":
			case "3.8.4":
			case "3.9.0":
			case "3.9.1":
			case "3.9.2":
			case "3.9.3":
			case "3.9.4":
			case "3.9.5":
			case "3.9.6":
			case "3.10.0":
				break;
			default:
				if (!version.includes("DEV")) console.log("Unknown map version: " + version);
        }
        
        this.intent = (map.intent != undefined ? map.intent : ((user) ? user.intent : 0.5));
		this.compute = new ComputeConfig(map.compute || {}, user);
		this.graphics = new GraphicsConfig(map.graphics || {}, user); 
        this.memory = new MemoryConfig(map.memory || {}, user);
        this.storage = new StorageConfig(map.storage || {});
		this.upload = new UploadConfig(map.upload || {});
		this.machineAssortment = map.machineAssortment || []
		this.notifications = new NotificationConfig(map.notifications || {});
		this.package = new PackageConfig(map.package || {});
		this.interactive = map.interactive == undefined ? false : map.interactive;
		this.annotation = map.annotation || "";
	}

	public copy(): OptumiConfig {
		return new OptumiConfig(JSON.parse(JSON.stringify(this)));
	}
}
