import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, lastValueFrom } from 'rxjs';


import { environment } from 'src/environments/environment';
import { PostOrientation } from '../types/Sensor';
import { Posture } from '../types/PostureScore';


@Injectable({
	providedIn: "root",
})
export class PostureService {

	
    constructor(private http: HttpClient) {}

	private endpoint = `${environment.API_ENDPOINT}internal-posture`;

    postInternalPosture(
        orientationWithUserId:PostOrientation,
        file: File
    ): Promise<Posture> {
        const fd = new FormData();
        fd.append("file", file);
        fd.append("orientation", JSON.stringify(orientationWithUserId))
        return lastValueFrom(this.http.post<Posture>(`${this.endpoint}/`, fd))
    };

    postOrientation(
        orientationWithUserId:PostOrientation
    ): Promise<Posture> {
        return lastValueFrom(this.http.post<Posture>(`${this.endpoint}/orientation/`, orientationWithUserId))
    };

    postOrientations(
        orientationsWithUserId:PostOrientation[]
    ): Promise<Posture[]> {
        if (orientationsWithUserId.length === 0) {
            return Promise.resolve([]);
        }
        return lastValueFrom(this.http.post<Posture[]>(`${this.endpoint}/orientation/list/`, orientationsWithUserId))
    }

    postVideo(
        userId: number,
        file: File
    ): Promise<Posture> {
        const fd = new FormData();
        fd.append("file", file);
        fd.append("user_id", JSON.stringify({id: userId}))
        return lastValueFrom(this.http.post<Posture>(`${this.endpoint}/video/`, fd))
    }
}