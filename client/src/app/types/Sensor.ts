export interface DeviceMotionEventiOS extends DeviceMotionEvent {
    requestPermission?: () => Promise<'granted' | 'denied'>;
}

export interface DeviceOrientationEventiOS extends DeviceOrientationEvent {
    requestPermission?: () => Promise<'granted' | 'denied'>;
}

export type Quaternion = {
    w: number;
    x: number;
    y: number;
    z: number;
}

export type Eular = {
    pitch: number;
    roll: number;
    yaw: number;
}

export type Orientation = {
    alpha: number | null;
    beta: number | null;
    gamma: number | null;
}

export type OrientationWithUserId = {
    userId: number
} & Orientation;

export type Motion = {
    x: number;
    y: number;
    z: number;
    pitch: number;
    yaw: number;
    roll: number;
    acceleration: {
        x: number | null | undefined,
        y: number | null | undefined,
        z: number | null | undefined,
        gravityX: number | null | undefined;
        gravityY: number | null | undefined;
        gravityZ: number | null | undefined;
        rotationX: number | null | undefined;
        rotationY: number | null | undefined;
        rotationZ: number | null | undefined;
    }
}

export type MotionWithUserId = {
    userId: number
} & Motion;