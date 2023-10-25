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
    k: number = 0.95;

    constructor(){
    }

    requestPermission() {
        const requestPermission = (DeviceOrientationEvent as unknown as DeviceMotionEventiOS).requestPermission;
        const iOS = typeof requestPermission === 'function';
        if (iOS) {
            requestPermission().then(res => {
                if (res === 'granted') {
                    this.parmitted = true;
                    this.starteMotionDetection();
                } else {
                    alert("動作と方向へのアクセスを許可してください");
                }
            }).catch(e => {
                this.parmitted = false
            });
        } else {
            this.parmitted = true;
            this.starteMotionDetection();
        }

        if(navigator && navigator.userAgent) {
            this.osCorrection = navigator.userAgent.indexOf("Android") === -1 ? 1 : -1;
        }
    }

    starteMotionDetection(){
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

            this.motion.x += (e.acceleration?.x ?? 0) * e.interval ** 2;
            this.motion.y += (e.acceleration?.y ?? 0) * e.interval ** 2;
            this.motion.z += (e.acceleration?.z ?? 0) * e.interval ** 2;

            const pitch = Math.cos(this.motion.roll)*(e.rotationRate?.alpha ?? 0)
                - Math.sin(this.motion.roll)*(e.rotationRate?.beta ?? 0);
            this.motion.pitch = this.conplementaryFilter(
                this.motion.pitch,
                pitch,
                this.motion.acceleration.gravityZ ?? 0,
                this.motion.acceleration.gravityY ?? 0,
                e.interval
            );
            const yaw = Math.sin(this.motion.roll) / Math.cos(this.motion.pitch) * (e.rotationRate?.alpha ?? 0)
                + Math.cos(this.motion.roll) / Math.cos(this.motion.pitch) * (e.rotationRate?.beta ?? 0);
            this.motion.yaw = this.conplementaryFilter(
                this.motion.yaw,
                yaw,
                this.motion.acceleration.gravityX ?? 0,
                this.motion.acceleration.gravityZ ?? 0,
                e.interval
            );
            const roll = (e.rotationRate?.gamma ?? 0)
                + Math.sin(this.motion.roll) * Math.sin(this.motion.pitch) / Math.cos(this.motion.pitch) * (e.rotationRate?.alpha ?? 0)
                + Math.cos(this.motion.roll) * Math.sin(this.motion.pitch) / Math.cos(this.motion.pitch) * (e.rotationRate?.beta ?? 0);
            this.motion.roll = this.conplementaryFilter(
                this.motion.roll,
                roll,
                this.motion.acceleration.gravityY ?? 0,
                this.motion.acceleration.gravityX ?? 0,
                e.interval
            );

            this.updatedAt = new Date();
        });
    }

    conplementaryFilter(ptheta: number, theta: number, gravityX: number, gravityY: number, dt: number): number {
        return this.k*(ptheta + theta*dt) + (1-this.k)*Math.atan2(gravityY, gravityX);
    }
}