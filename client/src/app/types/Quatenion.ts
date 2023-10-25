export type Quaternion = {
    x: number | null;
    y: number | null;
    z: number | null;
    w: number | null;
}

export type QuaternionWithUserId = {
    userId: number
} & Quaternion;