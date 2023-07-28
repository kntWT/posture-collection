
interface DeviceOrientationEventiOS extends DeviceOrientationEvent {
    requestPermission?: () => Promise<'granted' | 'denied'>;
}

type Orientation = {
    alpha: number | null;
    beta: number | null;
    gamma: number | null;
}

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
        const requestPermission = (DeviceOrientationEvent as unknown as DeviceOrientationEventiOS).requestPermission;
        const iOS = typeof requestPermission === 'function';
        if (iOS) {
            requestPermission().then(res => {
                if (res === 'granted') {
                    this.parmitted = true;
                    this.starteOrientationDetection();
                } else {
                    alert("動作と方向へのアクセスを許可してください");
                }
            }).catch(e => {
                this.parmitted = false
            });
        } else {
            this.parmitted = true;
            this.starteOrientationDetection();
        }

        if(navigator && navigator.userAgent) {
            this.osCorrection = navigator.userAgent.indexOf("Android") == -1 ? 0 : 90;
        }
    }

    starteOrientationDetection(){
        if(!window || !this.parmitted) return;

        window.addEventListener('deviceorientation',e => {
            const alpha = e.alpha ? (e.alpha + this.osCorrection) % 360 : null;
            const beta = e.beta;
            const gamma = e.gamma;
            this.orientation = {alpha, beta, gamma};
            this.updatedAt = new Date();
        });
    }
}