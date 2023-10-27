import { Motion, DeviceMotionEventiOS, Eular } from "src/app/types/Sensor";
import { highPassFilter, normalizeDegree, radianToDegree, lowPassFilter } from "./utils";


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

    requestPermission(startFlag: boolean = true): Promise<void> {
        const requestPermission = (DeviceOrientationEvent as unknown as DeviceMotionEventiOS).requestPermission;
        const iOS = typeof requestPermission === 'function';
        if(navigator && navigator.userAgent) {
            this.osCorrection = navigator.userAgent.indexOf("Android") === -1 ? 1 : -1;
        }
        return new Promise((resolve, reject) => {
            if (iOS) {
                requestPermission().then(res => {
                    if (res === 'granted') {
                        this.parmitted = true;
                        if (startFlag) {
                            this.startMotionDetection();
                        }
                        resolve();
                    } else {
                        alert("動作と方向へのアクセスを許可してください");
                        reject();
                    }
                }).catch(e => {
                    this.parmitted = false
                    reject();
                });
            } else {
                this.parmitted = true;
                if (startFlag) {
                    this.startMotionDetection();
                }
                resolve();
            }
        });

    }

    startMotionDetection(){
        if(!window || !this.parmitted) return;

        window.addEventListener('devicemotion', e => {
            const dt = e.interval * 1000;
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
            this.motion.x = highPassFilter(this.k, this.motion.x, (e.acceleration?.x ?? 0) * dt);
            this.motion.y = highPassFilter(this.k, this.motion.y, (e.acceleration?.y ?? 0) * dt);
            this.motion.z = highPassFilter(this.k, this.motion.z, (e.acceleration?.z ?? 0) * dt);

            this.motion = {...this.motion, ...this.getEularAngle(e)};

            this.updatedAt = new Date();
        });
    }

    getEularAngle(motionEvent: DeviceMotionEvent): Eular {
        const dt = motionEvent.interval * 1000;
        const rollAcc = highPassFilter(
            this.k,
            this.motion.roll,
            (motionEvent.rotationRate?.gamma ?? 0)
                + Math.sin(this.motion.roll) * Math.sin(this.motion.pitch) / Math.cos(this.motion.pitch) * (motionEvent.rotationRate?.alpha ?? 0)
                + Math.cos(this.motion.roll) * Math.sin(this.motion.pitch) / Math.cos(this.motion.pitch) * (motionEvent.rotationRate?.beta ?? 0)
        );
        const rollGrav = normalizeDegree(
            radianToDegree(
                Math.atan2(
                    motionEvent.accelerationIncludingGravity?.y ?? 0,
                    motionEvent.accelerationIncludingGravity?.x ?? 0
                )
            ) - 90
        );
        const pitchAcc = highPassFilter(
            this.k,
            this.motion.pitch,
            Math.cos(this.motion.roll)*(motionEvent.rotationRate?.alpha ?? 0)
                - Math.sin(this.motion.roll)*(motionEvent.rotationRate?.beta ?? 0)
        );
        const pitchGrav = normalizeDegree(
            radianToDegree(
                Math.atan2(
                    motionEvent.accelerationIncludingGravity?.z ?? 0,
                    motionEvent.accelerationIncludingGravity?.y ?? 0
                )
            )
        );
        const yawAcc = highPassFilter(
            this.k,
            this.motion.yaw,
            Math.sin(this.motion.roll) / Math.cos(this.motion.pitch) * (motionEvent.rotationRate?.alpha ?? 0)*dt
                + Math.cos(this.motion.roll) / Math.cos(this.motion.pitch) * (motionEvent.rotationRate?.beta ?? 0)*dt
        );
        const yawGrav = normalizeDegree(
            radianToDegree(
                Math.atan2(
                    motionEvent.accelerationIncludingGravity?.x ?? 0,
                    motionEvent.accelerationIncludingGravity?.z ?? 0
                )
            )
        );
        // const roll = this.complementaryFilter(this.motion.roll, rollAcc*dt, rollGrav);
        // const roll = rollAcc;
        const roll = lowPassFilter(this.k, this.motion.roll, rollGrav);
        // const pitch = this.complementaryFilter(this.motion.pitch, pitchAcc*dt, pitchGrav);
        // const pitch = pitchAcc;
        const pitch = lowPassFilter(this.k, this.motion.pitch, pitchGrav);
        // const yaw = this.complementaryFilter(yawAcc, yawGrav);
        const yaw = yawAcc;
        // const yaw = this.lowPassFilter(this.motion.yaw, yawGrav);

        return {
            pitch,
            yaw,
            roll
        };
    }
}