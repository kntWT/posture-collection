import { DeviceMotionDetector } from "./DeviceMotionDetector";
import { DeviceOrientationDetector } from "./DeviceOrientationDetector";
import { Eular, Quaternion } from "src/app/types/Sensor";
import { toQuaternion, toEular, radianToDegree, degreeToRadian } from "./utils";

export class DeviceSensor {

    motionDetector: DeviceMotionDetector | null = null;
    orientationDetector: DeviceOrientationDetector | null = null;
    eular: Eular = {
        pitch: 0,
        roll: 0,
        yaw: 0
    };
    test: Eular = {
        roll: 20,
        pitch: 40,
        yaw: 52
    };
    message2: string = "";

    constructor() {
        this.test.pitch = degreeToRadian(this.test.pitch);
        this.test.roll = degreeToRadian(this.test.roll);
        this.test.yaw = degreeToRadian(this.test.yaw);
        const q = toQuaternion(this.test);
        this.test = toEular(q);
        this.test.pitch = radianToDegree(this.test.pitch);
        this.test.roll = radianToDegree(this.test.roll);
        this.test.yaw = radianToDegree(this.test.yaw);
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
            this.eular.yaw = this.orientationDetector.getOrientation(e).gamma || 0;
        });

        window.addEventListener('devicemotion', e => {
            if (!this.motionDetector) return;
            const eular: Eular = this.motionDetector.getEularAngle(e);

            this.eular.pitch = eular.pitch;
            this.eular.roll = eular.roll;
            this.message2 = "orientationDetector: " + eular.roll + "\n";
        });
    }

    isPermitted() {
        return this.motionDetector?.parmitted && this.orientationDetector?.parmitted;
    }

}