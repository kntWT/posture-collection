import { Eular, Quaternion } from "src/app/types/Sensor";

// XYZ order
// Eular must be raqian
const toQuaternion = (e: Eular) : Quaternion => {
    const cr = Math.cos(e.roll * 0.5);
    const sr = Math.sin(e.roll * 0.5);
    const cp = Math.cos(e.pitch * 0.5);
    const sp = Math.sin(e.pitch * 0.5);
    const cy = Math.cos(e.yaw * 0.5);
    const sy = Math.sin(e.yaw * 0.5);

    return {
        w: cr * cp * cy + sr * sp * sy,
        x: sr * cp * cy - cr * sp * sy,
        y: cr * sp * cy + sr * cp * sy,
        z: cr * cp * sy - sr * sp * cy
    };
}

// XYZ order
// Eular will be raqian
const toEular = (q: Quaternion) : Eular =>{
    const w = q.w;
    const x = q.x;
    const y = q.y;
    const z = q.z;
  
    // クォータニオンをオイラー角に変換
    const t0 = 2 * (w*x + y*z);
    const t1 = 1 - 2 * (x*x + y*y);
    const roll = Math.atan2(t0, t1);

    const t2 = 2 * (w*y - z*x);
    const pitch = Math.abs(t2) >= 1 ? Math.sin(t2)*(Math.PI / 2) : Math.asin(t2);

    const t3 = 2 * (w*z + x*y);
    const t4 = 1 - 2 * (y*y + z*z);
    const yaw = Math.atan2(t3, t4);

    return { pitch, roll, yaw };
}

// 相補フィルタ
const complementaryFilter = (k: number, thetaA: number, thetaB: number): number => {
    return k*thetaA + (1-k)*thetaB;
}

//ローパスフィルタ
const lowPassFilter = (k: number, pvalue: number, value: number): number => {
    return k*pvalue + (1-k)*value;
}

// ハイパスフィルタ
const highPassFilter = (k: number, pvalue: number, value: number): number => {
    return value - lowPassFilter(k, pvalue, value);
}

const degreeToRadian = (degree: number): number => {
    return degree * Math.PI / 180;
}

const eularToRadian = (eular: Eular): Eular => {
    return {
        pitch: degreeToRadian(eular.pitch),
        roll: degreeToRadian(eular.roll),
        yaw: degreeToRadian(eular.yaw)
    };
}

const radianToDegree = (radian: number): number => {
    return radian * 180 / Math.PI;
}

const eularToDegree = (eular: Eular): Eular => {
    return {
        pitch: radianToDegree(eular.pitch),
        roll: radianToDegree(eular.roll),
        yaw: radianToDegree(eular.yaw)
    };
}

// ~ -180, 180 ~ -> -180 ~ 180
const normalizeDegree = (degree: number): number => {
    const sign = degree >= 0 ? 1 : -1;
    return (180 - Math.abs(degree)) * sign;
}

export {
    toQuaternion,
    toEular,
    complementaryFilter,
    lowPassFilter,
    highPassFilter,
    degreeToRadian,
    eularToRadian,
    radianToDegree,
    eularToDegree,
    normalizeDegree
}