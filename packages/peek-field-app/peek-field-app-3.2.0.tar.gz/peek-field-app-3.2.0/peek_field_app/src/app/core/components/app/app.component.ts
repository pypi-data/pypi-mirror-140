import { Component } from "@angular/core";
import {
    NgLifeCycleEvents,
    VortexService,
    VortexStatusService,
} from "@synerty/vortexjs";
import { DeviceStatusService } from "@peek/peek_core_device";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { takeUntil } from "rxjs/operators";

@Component({
    selector: "app-component",
    templateUrl: "app.component.html",
    styleUrls: ["app.component.scss"],
})
export class AppComponent extends NgLifeCycleEvents {
    fullScreen = false;

    constructor(
        public balloonMsg: BalloonMsgService,
        private vortexService: VortexService,
        private vortexStatusService: VortexStatusService,
        private deviceStatusService: DeviceStatusService
    ) {
        super();
        vortexStatusService.errors
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((msg: string) => balloonMsg.showError(msg));

        vortexStatusService.warning
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((msg: string) => balloonMsg.showWarning(msg));
    }

    setBalloonFullScreen(enabled: boolean): void {
        this.fullScreen = enabled;
    }

    showLoading(): boolean {
        return this.deviceStatusService.isLoading;
    }
}
