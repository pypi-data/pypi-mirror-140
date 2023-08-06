import { Injectable } from "@angular/core";
import { BehaviorSubject, combineLatest, Observable } from "rxjs";
import {
    DeviceGpsLocationService,
    DeviceGpsLocationTuple,
} from "@peek/peek_core_device";
import { UserService } from "@peek/peek_core_user";
import { Capacitor, Plugins } from "@capacitor/core";
import { DeviceTupleService } from "../device-tuple.service";
import { GpsLocationUpdateTupleAction } from "./GpsLocationUpdateTupleAction";
import { DeviceEnrolmentService } from "../../device-enrolment.service";
import { DeviceBackgroundService } from "../device-background.service";
import { BackgroundGeolocationPlugin } from "@capacitor-community/background-geolocation";

const BackgroundGeolocation =
    Plugins.BackgroundGeolocation as BackgroundGeolocationPlugin;

const { Geolocation, Modals } = Plugins;

@Injectable()
export class PrivateDeviceGpsLocationService extends DeviceGpsLocationService {
    private _location$ = new BehaviorSubject<DeviceGpsLocationTuple | null>(
        null
    );
    private gpsWatchId: string | null;
    private lastSeenPositionTupleAction: GpsLocationUpdateTupleAction;

    constructor(
        private tupleService: DeviceTupleService,
        private deviceService: DeviceEnrolmentService,
        private deviceBackgroundService: DeviceBackgroundService,
        private userService: UserService
    ) {
        super();

        combineLatest(
            this.userService.loggedInStatus,
            this.deviceService.deviceInfoObservable()
        ).subscribe(async ([isLoggedIn, deviceInfo]) => {
            if (isLoggedIn && deviceInfo.isEnrolled) {
                if (!this.gpsWatchId) {
                    this.startLocationListener();
                }
            } else {
                if (this.gpsWatchId) {
                    this.stopLocationListener();
                }
            }
        });
    }

    get location$(): Observable<DeviceGpsLocationTuple | null> {
        return this._location$.asObservable();
    }

    get location(): DeviceGpsLocationTuple | null {
        return this._location$.getValue();
    }

    private get _location(): DeviceGpsLocationTuple | null {
        return this._location$.getValue();
    }

    private set _location(value) {
        this._location$.next(value);
    }

    private startLocationListener(): void {
        if (Capacitor.isNative) {
            this.gpsWatchId = BackgroundGeolocation.addWatcher(
                {
                    backgroundMessage:
                        "Allow Peek track this devices GPS location.",
                    backgroundTitle: "Peek GPS Feature",
                    requestPermissions: true,
                    stale: false,
                    distanceFilter: 25,
                },
                (coords, error) => {
                    if (error) {
                        if (error.code === "NOT_AUTHORIZED") {
                            this.handleLocationPermission();
                        }
                        return console.log(error);
                    }
                    if (coords) {
                        this.updateLocation({ coords });
                    }
                }
            );
        } else {
            Geolocation.getCurrentPosition()
                .then((position) => {
                    if (position) {
                        this.updateLocation(position);
                    }
                })
                .catch((err) => {
                    console.log("Cannot get current GPS position.");
                });

            this.gpsWatchId = Geolocation.watchPosition(
                { enableHighAccuracy: true },
                (position, err) => {
                    if (position) {
                        this.updateLocation(position);
                    }
                }
            );
        }
    }

    private handleLocationPermission(): void {
        Modals.confirm({
            title: "Location Required",
            message:
                "This app needs your location, " +
                "but does not have permission.\n\n" +
                "Do you want to enable GPS support now?",
        }).then(({ value }) => {
            if (value) {
                BackgroundGeolocation.openSettings();
            }
        });
    }

    private stopLocationListener(): void {
        if (Capacitor.isNative) {
            BackgroundGeolocation.removeWatcher({ id: this.gpsWatchId });
        } else {
            Geolocation.clearWatch({ id: this.gpsWatchId });
        }
        this.gpsWatchId = null;
    }

    private updateLocation(position): void {
        const now = new Date(); // In datetime with timezone

        // Send to Peek Logic
        const action = new GpsLocationUpdateTupleAction();
        action.latitude = position.coords.latitude;
        action.longitude = position.coords.longitude;
        action.updateType = GpsLocationUpdateTupleAction.ACCURACY_FINE;
        action.datetime = now;
        action.deviceToken = this.deviceService.enrolmentToken();
        this.lastSeenPositionTupleAction = action;
        this.tupleService.tupleOfflineAction.pushAction(action);

        // Update location observable
        const location = new DeviceGpsLocationTuple();
        location.latitude = position.coords.latitude;
        location.longitude = position.coords.longitude;
        location.datetime = now;
        location.deviceToken = this.deviceService.enrolmentToken();
        this._location = location;
    }
}
