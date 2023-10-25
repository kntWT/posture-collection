import { Motion } from "src/app/types/Motion";

interface DeviceMotionEventiOS extends DeviceMotionEvent {
    requestPermission?: () => Promise<'granted' | 'denied'>;
}

export class DeviceMotionDetector {
    motion: Motion = {
        x: 0,
        y: 0,
        z: 0,
        pitch: 0,
        roll: 0,
        yaw: 0,
        acceleration: {
            x: null,
            y: null,
            z: null,
            gravityX: null,
            gravityY: null,
            gravityZ: null,
            rotationX: null,
            rotationY: null,
            rotationZ: null
        }
    };
    osCorrection: number = 0; // to correct alpha value on Android device
    parmitted: boolean = false;
    updatedAt: Date | null = null;
    k: number = 0.9;

    constructor(){
    }

    requestPermission() {
        const requestPermission = (DeviceOrientationEvent as unknown as DeviceMotionEventiOS).requestPermission;
        const iOS = typeof requestPermission === 'function';
        if (iOS) {
            requestPermission().then(res => {
                if (res === 'granted') {
                    this.parmitted = true;
                    this.startMotionDetection();
                } else {
                    alert("動作と方向へのアクセスを許可してください");
                }
            }).catch(e => {
                this.parmitted = false
            });
        } else {
            this.parmitted = true;
            this.startMotionDetection();
        }

        if(navigator && navigator.userAgent) {
            this.osCorrection = navigator.userAgent.indexOf("Android") === -1 ? 1 : -1;
        }
    }

    startMotionDetection(){
        if(!window || !this.parmitted) return;

        window.addEventListener('devicemotion', e => {
            this.motion.acceleration.x = e.acceleration?.x;
            this.motion.acceleration.y = e.acceleration?.y;
            this.motion.acceleration.z = e.acceleration?.z;
            this.motion.acceleration.gravityX = e.accelerationIncludingGravity?.x;
            this.motion.acceleration.gravityY = e.accelerationIncludingGravity?.y;
            this.motion.acceleration.gravityZ = e.accelerationIncludingGravity?.z;
            this.motion.acceleration.rotationX = e.rotationRate?.alpha;
            this.motion.acceleration.rotationY = e.rotationRate?.beta;
            this.motion.acceleration.rotationZ = e.rotationRate?.gamma;

            // this.motion.x += (e.acceleration?.x ?? 0) * (e.interval ** 2);
            this.motion.x = this.lowPassFilter(this.motion.x, (e.acceleration?.x ?? 0) * e.interval);
            this.motion.y = this.lowPassFilter(this.motion.y, (e.acceleration?.y ?? 0) * e.interval);
            this.motion.z = this.lowPassFilter(this.motion.z, (e.acceleration?.z ?? 0) * e.interval);

            const pitchAcc = Math.cos(this.motion.roll)*(e.rotationRate?.alpha ?? 0)
                - Math.sin(this.motion.roll)*(e.rotationRate?.beta ?? 0);
            const pitchGrav = this.normalizeDegree(
                this.radianToDegree(
                    Math.atan2(
                        this.motion.acceleration.gravityZ ?? 0,
                        this.motion.acceleration.gravityY ?? 0
                    )
                )
            );
            const yawAcc = Math.sin(this.motion.roll) / Math.cos(this.motion.pitch) * (e.rotationRate?.alpha ?? 0)
                + Math.cos(this.motion.roll) / Math.cos(this.motion.pitch) * (e.rotationRate?.beta ?? 0);
            const yawGrav = this.normalizeDegree(
                this.radianToDegree(
                    Math.atan2(
                        this.motion.acceleration.gravityX ?? 0,
                        this.motion.acceleration.gravityZ ?? 0
                    )
                )
            );
            const rollAcc = (e.rotationRate?.gamma ?? 0)
                + Math.sin(this.motion.roll) * Math.sin(this.motion.pitch) / Math.cos(this.motion.pitch) * (e.rotationRate?.alpha ?? 0)
                + Math.cos(this.motion.roll) * Math.sin(this.motion.pitch) / Math.cos(this.motion.pitch) * (e.rotationRate?.beta ?? 0);
            const rollGrav = this.normalizeDegree(
                this.radianToDegree(
                    Math.atan2(
                        this.motion.acceleration.gravityY ?? 0,
                        this.motion.acceleration.gravityX ?? 0
                    )
                ) - 90
            );
            // this.motion.pitch = this.complementaryFilter(this.motion.pitch, pitchAcc, pitchGrav, e.interval);
            this.motion.pitch = this.lowPassFilter(this.motion.pitch, pitchGrav);
            // this.motion.yaw = this.complementaryFilter(this.motion.yaw, yawAcc, yawGrav, e.interval);
            this.motion.yaw = this.lowPassFilter(this.motion.yaw, yawGrav);
            // this.motion.roll = this.complementaryFilter(this.motion.roll, rollAcc, rollGrav, e.interval);
            this.motion.roll = this.lowPassFilter(this.motion.roll, rollGrav);

            this.updatedAt = new Date();
        });
    }

    // 相補フィルタ
    complementaryFilter(ptheta: number, thetaA: number, thetaB: number, dt: number): number {
        return this.k*(ptheta + thetaA*dt) + (1-this.k)*thetaB;
    }

    //ローパスフィルタ
    lowPassFilter(pvalue: number, value: number): number {
        return this.k*pvalue + (1-this.k)*value;
    }

    degreeToRadian(degree: number): number {
        return degree * Math.PI / 180;
    }

    radianToDegree(radian: number): number {
        return radian * 180 / Math.PI;
    }

    // ~ -180, 180 ~ -> -180 ~ 180
    normalizeDegree(degree: number): number {
        const sign = degree >= 0 ? 1 : -1;
        return (180 - Math.abs(degree)) * sign;
    }
}