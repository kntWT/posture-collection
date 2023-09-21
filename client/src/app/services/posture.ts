import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { tap } from 'rxjs/operators';
import { environment } from 'src/environments/environment';
import { OrientationWithUserId } from '../types/Orientation';
import { calibrate } from '../store/user/actions';

@Injectable({
	providedIn: "root",
})
export class PostureService {

	
    constructor(private http: HttpClient) {}

	private endpoint = `${environment.API_ENDPOINT}internal-posture`;

    post(
        orientationWithUserId:( OrientationWithUserId & {createdAt: string, calibrateFlag: boolean} ),
        file: File
    ) {
        const fd = new FormData();
        fd.append("file", file);
        fd.append("orientation", JSON.stringify(orientationWithUserId))
        return this.http
            .post(`${this.endpoint}/`, fd)
            .pipe(tap(posture => console.log(posture)))
    }
}