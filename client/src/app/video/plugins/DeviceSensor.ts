import { DeviceMotionDetector } from "./DeviceMotionDetector";
import { DeviceOrientationDetector } from "./DeviceOrientationDetector";
import { Eular, Quaternion } from "src/app/types/Sensor";
import { toQuaternion, eularToDegree, eularToRadian } from "./utils";

export class DeviceSensor {

    motionDetector: DeviceMotionDetector | null = null;
    orientationDetector: DeviceOrientationDetector | null = null;
    eular: Eular = {
        pitch: 0,
        roll: 0,
        yaw: 0
    };
    quaternion: Quaternion = toQuaternion(this.eular);

    constructor() {
    }

    async requestOrientationPermission() {
        this.orientationDetector = new DeviceOrientationDetector();
        await this.orientationDetector.requestPermission(false);
        if (this.isPermitted()) {
            this.startDetection();
        }
    }

    async requestMotionPermission() {
        this.motionDetector = new DeviceMotionDetector();
        await this.motionDetector.requestPermission(false);
        if (this.isPermitted()) {
            this.startDetection();
        }
    }

    startDetection() {
        if (!this.isPermitted) return;

        window.addEventListener('deviceorientation', e => {
            if (!this.orientationDetector) return;
            
            this.eular.pitch = this.orientationDetector.getOrientation(e).beta || 0;
            this.eular.yaw = this.orientationDetector.getOrientation(e).gamma || 0;

            this.quaternion = toQuaternion(eularToRadian(this.eular));
        });

        window.addEventListener('devicemotion', e => {
            if (!this.motionDetector) return;
            const eular: Eular = this.motionDetector.getEularAngle(e);

            // this.eular.pitch = eular.pitch;
            this.eular.roll = eular.roll;

            this.quaternion = toQuaternion(eularToRadian(this.eular));
        });
    }

    isPermitted() {
        return this.motionDetector?.parmitted && this.orientationDetector?.parmitted;
    }

}