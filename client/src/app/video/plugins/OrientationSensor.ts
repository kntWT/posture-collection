import { Quaternion } from "src/app/types/Quatenion";

export class DeviceQuaternionDetector {
    sensor: OrientationSensor | null = null;
    quaternion: Quaternion = {
        x: null,
        y: null,
        z: null,
        w: null
    };
    parmitted: boolean = false;
    updatedAt: Date | null = null;

    constructor(){
        const options: MotionSensorOptions = { frequency: 100, referenceFrame: "device" };
        this.sensor = new AbsoluteOrientationSensor(options);
    }

    requestPermission() {
        Promise.all([
            navigator.permissions.query({ name: "accelerometer" as PermissionName }),
            navigator.permissions.query({ name: "magnetometer" as PermissionName }),
            navigator.permissions.query({ name: "gyroscope" as PermissionName }),
        ]).then((results) => {
            if (this.sensor === null) return;
            if (results.every((result) => result.state === "granted")) {
                this.sensor.start();
                this.sensor,addEventListener('reading', this.updateQuaternion.bind(this));
            } else {
                console.log("No permissions to use AbsoluteOrientationSensor.");
            }
        });
    }

    updateQuaternion(){
        if (this.sensor === null || this.sensor.quaternion === undefined) return;
        this.quaternion = {
            x: this.sensor.quaternion[0],
            y: this.sensor.quaternion[1],
            z: this.sensor.quaternion[2],
            w: this.sensor.quaternion[3]
        };
        this.updatedAt = new Date();
    }

    toEularAngle(){
        const q = this.quaternion;
        if (!q.x || !q.y || !q.z || !q.w) return;
        const pitch = Math.atan2(2.0 * (q.y * q.z + q.x * q.w), q.x * q.x + q.y * q.y - q.z * q.z - q.w * q.w);
        const roll = Math.asin(-2.0 * (q.y * q.w - q.x * q.z));
        const yaw = Math.atan2(2.0 * (q.x * q.y + q.z * q.w), q.x * q.x - q.y * q.y - q.z * q.z + q.w * q.w);
        return {pitch, roll, yaw};
    }
}