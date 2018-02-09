import request from '../utils/request';
import qs from 'qs';

export async function queryApiIndex() {
    console.log('/api')
    return await request(`/api`)
}

export async function queryItem(params) {
    console.log('/api/items')
    return await request(`/api/items?${qs.stringify(params)}`);
}
