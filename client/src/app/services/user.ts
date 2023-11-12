import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { User, UserBasicInfo, UserCalibrateion } from '../types/User';
import { tap } from 'rxjs/operators';
import { environment } from 'src/environments/environment';

@Injectable({
	providedIn: "root",
})
export class UserService {
	
    constructor(private http: HttpClient) {}

	private endpoint = `${environment.API_ENDPOINT}user`;

	authHeader = (props: UserBasicInfo) => ({
		headers: new HttpHeaders({ 'Authorization': `Basic ${btoa(`${props.name}:${props.password}`)}` }),
	});

	signup(props: UserBasicInfo) {
		return this.http
			.post<User>(`${this.endpoint}/`, props)
			.pipe(tap(user => console.log('sing up success name:', user.name)));
	}

	login(props: UserBasicInfo) {
		return this.http.get<User>(`${this.endpoint}/auth/`, this.authHeader(props));
	}

    loginAsGuest() {
        return this.http.get<User>(`${this.endpoint}/guest/`);
    }

	calibrate(props: UserCalibrateion) {
		return this.http.put<User>(
			`${this.endpoint}/calibration/internal-posture/${props.id}`,
			{
				internal_posture_calibration_id: props.internalPostureCalibrationId,
				neck_to_nose_standard: props.neckToNoseStandard ?? null
			}
		);
	}
}