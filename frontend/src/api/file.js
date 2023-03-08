import request from './axios'

// 获取PDF
export function getFileImageList(paper_id) {
    return request({
        url: `http://127.0.0.1:8000/api/v1/table/${paper_id}/images`,
        method: 'get',
        // responseType: 'blob'
    })
}

// 上传文件
export function uploadFile(data) {
    return request({
        url: `http://127.0.0.1:8000/api/v1/file/file`,
        // url: `https://127.0.0.1:8000/api/v1/paper_list/file`,
        headers: {
            'Content-Type': 'multipart/form-data'
        },
        method: 'put',
        data,
    })
}

// 获取table信息
export function getTableInfo(paper_id) {
    return request({
        url: 'https://127.0.0.1:8000/api/v2/table/parse_pdf',
        params: {
            paper_id
        },
        method: 'get'
    })
}


// export function getFileImageList(project_id, paper_id) {
//     return request({
//         url: `/v1/paper/${project_id}/${paper_id}/images`,
//         method: 'get'
//     })
// }

// 获取table外框线
export function getTableOutLine(data) {
    return request({
        url: `http://127.0.0.1:8000/api/v1/table/`,
        method: 'post',
        data
    })
}

// 更新表格外框线
export function updateTableOutLine(data) {
    return request({
        url: `https://127.0.0.1:8000/api/v2/table/update_outline`,
        method: 'put',
        data
    })
}

// 删除表格外框线
export function deleteTableOutLine(data) {
    return request({
        url: `https://127.0.0.1:8000/api/v2/table/delete_outlines`,
        method: 'delete',
        data
    })
}

// 获取表格内框线
export function getTableInnerLine(paper_id, data) {
    return request({
        url: `http://127.0.0.1:8000/api/v1/table/${paper_id}/cell`,
        method: 'post',
        data
    })
}

// 获取表格图片
export function getTableImage(paper_id, data) {
    return request({
        url: `http://127.0.0.1:8000/api/v1/table/${paper_id}/image_outlined`,
        method: 'post',
        data
    })
}

// 更改表格内框线
export function updateInnerLine(project_id, paper_id, table_id, data) {
    return request({
        url: `https://127.0.0.1:8000/api/v2/table/cell`,
        method: 'put',
        data
    })
}

// 获取表格内容
export function getTableContent(paper_id, data) {
    return request({
        url: `http://127.0.0.1:8000/api/v1/table/${paper_id}/draw`,
        method: 'post',
        data
    })
}

// 下载表格
export function downloadTable(paper_id, trans_flag, data) {
    return request({
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        },
        url: `http://127.0.0.1:8000/api/v1/table/${paper_id}/${trans_flag}/excel`,
        method: 'post',
        data,
        responseType: 'blob'
    })
}

// 行列互换
export function tableRowToCol(project_id, paper_id, table_id, data) {
    return request({
        url: `https://127.0.0.1:8000/api/v2/table/${project_id}/${paper_id}/${table_id}/info`,
        method: 'put',
        data
    })
}

// 保存文本内容
export function updateTableContent(project_id, paper_id, table_id, data) {
    return request({
        url: `https://127.0.0.1:8000/api/v2/table/${project_id}/${paper_id}/${table_id}/content`,
        method: 'put',
        data
    })
}