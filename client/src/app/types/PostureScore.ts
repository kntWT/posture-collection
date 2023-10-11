export type PostureScore = {
    neckLength: number;
    headAngle: number;
};

export type Posture = {
    id:number; 
    user_id: number;
    file_name: string;
    orientation_alpha: number | null;
    orientation_beta: number | null;
    orientation_gamma: number | null;
    pitch: number | null;
    yaw: number | null;
    roll: number | null;
    nose_x: number | null;
    nose_y: number | null;
    neck_x: number | null;
    neck_y: number | null;
    neck_to_nose: number | null;
    standard_dist: number | null;
    calibrate_flag: boolean;
    created_at: Date;
}