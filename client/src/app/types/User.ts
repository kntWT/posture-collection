export type User = {
    id: number;
    name: string;
    password: string;
    neckToNoseStandard?: number | null;
    createdAt: string;
}

export type UserBasicInfo = {
    name: string;
    password: string;
}

export type UserCalibrateion = {
    id: number;
    neckToNoseStandard?: number | null;
    internalPostureCalibrationId: number;
}