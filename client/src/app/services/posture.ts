import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, lastValueFrom } from 'rxjs';


import { environment } from 'src/environments/environment';
import { OrientationWithUserId } from '../types/Sensor';
import { Posture } from '../types/PostureScore';

@Injectable({
	providedIn: "root",
})
export class PostureService {

	
    constructor(private http: HttpClient) {}

	private endpoint = `${environment.API_ENDPOINT}internal-posture`;

    post(
        orientationWithUserId:( OrientationWithUserId & {createdAt: string, calibrateFlag: boolean} ),
        file: File
    ): Promise<Posture> {
        const fd = new FormData();
        fd.append("file", file);
        fd.append("orientation", JSON.stringify(orientationWithUserId))
        return lastValueFrom(this.http.post<Posture>(`${this.endpoint}/`, fd))
    }
}