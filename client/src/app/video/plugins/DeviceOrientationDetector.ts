import { Orientation, DeviceOrientationEventiOS, Eular } from "src/app/types/Sensor";

export class DeviceOrientationDetector {
    orientation: Orientation = {
        alpha: null,
        beta: null,
        gamma: null
    };
    osCorrection: number = 0; // to correct alpha value on Android device
    parmitted: boolean = false;
    updatedAt: Date | null = null;

    constructor(){
    }

    async requestPermission(startFlag: boolean = true): Promise<void> {
        const requestPermission = (DeviceOrientationEvent as unknown as DeviceOrientationEventiOS).requestPermission;
        const iOS = typeof requestPermission === 'function';
        if(navigator && navigator.userAgent) {
            this.osCorrection = navigator.userAgent.indexOf("Android") === -1 ? 0 : 90;
        }

        return new Promise((resolve, reject) => {
            if (iOS) {
                requestPermission().then(res => {
                    if (res === 'granted') {
                        this.parmitted = true;
                        if (startFlag) {
                            this.starteOrientationDetection();
                        }
                    } else {
                        alert("動作と方向へのアクセスを許可してください");
                    }
                    resolve();
                }).catch(e => {
                    this.parmitted = false
                    reject();
                });
            } else {
                this.parmitted = true;
                if (startFlag) {
                    this.starteOrientationDetection();
                }
                resolve();
            }
        });
    }

    starteOrientationDetection(){
        if(!window || !this.parmitted) return;

        window.addEventListener('deviceorientation', e => {
            const alpha = e.alpha ? (e.alpha + this.osCorrection) % 360 : null;
            const beta = e.beta;
            const gamma = e.gamma;
            this.orientation = {alpha, beta, gamma};
            this.updatedAt = new Date();
        });
    }

    getOrientation(orientationEvent: DeviceOrientationEvent): Orientation {
        const alpha: number = (orientationEvent.alpha || 0) + this.osCorrection % 360;
        const beta: number = orientationEvent.beta || 0;
        const gamma: number = orientationEvent.gamma || 0;
        return {alpha, beta, gamma};
    }

}