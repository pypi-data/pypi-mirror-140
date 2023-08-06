import {
    addTupleType,
    Tuple,
    TupleOfflineStorageService,
    TupleSelector,
} from "@synerty/vortexjs";
import { deviceTuplePrefix } from "../PluginNames";
import { Md5 } from "ts-md5/dist/md5";
import { DeviceTypeEnum, HardwareInfoI } from "./hardware-info.abstract";
import { isField } from "./is-field.mweb";
import { Capacitor } from "@capacitor/core";

@addTupleType
class DeviceUuidTuple extends Tuple {
    public static readonly tupleName = deviceTuplePrefix + "DeviceUuidTuple";

    uuid: string;

    constructor() {
        super(DeviceUuidTuple.tupleName);
    }
}

export function webUuid(
    tupleStorage: TupleOfflineStorageService
): Promise<string> {
    let tupleSelector = new TupleSelector(DeviceUuidTuple.tupleName, {});

    // We don't need a real good way of getting the UUID, Peek just assigns it a token
    let browser = navigator.userAgent.substr(
        0,
        navigator.userAgent.indexOf(" ")
    );
    let uuid = <string>Md5.hashStr(`${browser} ${new Date().toString()}`);

    return <any>(
        tupleStorage
            .loadTuples(tupleSelector)
            .then((tuples: DeviceUuidTuple[]) => {
                // If we have a UUID already, then use that.
                if (tuples.length != 0) {
                    return tuples[0].uuid;
                }

                // Create a new tuple to store
                let newTuple = new DeviceUuidTuple();
                newTuple.uuid = uuid;

                // Store the UUID, and upon successful storage, return the generated uuid
                return tupleStorage
                    .saveTuples(tupleSelector, [newTuple])
                    .then(() => uuid);
            })
    );
}

export class HardwareInfo extends HardwareInfoI {
    constructor(private tupleStorage: TupleOfflineStorageService) {
        super();
    }

    uuid(): Promise<string> {
        return webUuid(this.tupleStorage);
    }

    description(): string {
        return navigator.userAgent;
    }

    deviceType(): DeviceTypeEnum {
        // Field
        if (isField) {
            switch (Capacitor.getPlatform()) {
                case "ios":
                    return DeviceTypeEnum.FIELD_IOS;
                case "android":
                    return DeviceTypeEnum.FIELD_ANDROID;
                case "web":
                default:
                    return DeviceTypeEnum.MOBILE_WEB;
            }
        }
        // Office
        else {
            return DeviceTypeEnum.DESKTOP_WEB;
        }
    }
}
