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