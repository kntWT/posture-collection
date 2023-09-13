export type Orientation = {
    alpha: number | null;
    beta: number | null;
    gamma: number | null;
}

export type OrientationWithUserId = {
    userId: number
} & Orientation;