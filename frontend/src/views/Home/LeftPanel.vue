<template>
  <div style="height:100%;">
    <div style="height: 100%" v-if="pdfImgList.length">
      <ul>
        <!-- <li v-for="(item, index) in resultList" :key="index + 'tabel-img'" tabindex="0" class="pdf-img-box" @dblclick="deleteCropper(index)" @mousedown="mouseDown($event, index)" @keydown="keyDown($event, index)" @contextmenu.prevent="showContextMenu($event, index)">
          <img :class="'pdf-img-'+index" class="pdf-img" :src="item.url" alt="" srcset="">
          <canvas :id="'pdf-canvas-' + index" width="100%" height="100%" />
        </li> -->
        <!-- tabindex="0" @keydown="keyDown($event, index)" -->
        <li v-for="(item, index) in pdfImgList" id="pdf-img-box" :key="index + 'pdf-img'" class="pdf-img-box" @contextmenu.prevent="showContextMenu($event)">
          <img :id="'pdf-img-'+item.id" class="pdf-img" alt="">
          <canvas :id="'canvas-'+item.id" :data-index="index" class="img-canvas" />
        </li>
      </ul>
      <ul v-if="isShowContextMenu" :style="{'left': menuX + 'px', 'top': menuY + 'px' }" class="context-menu">
        <li v-for="item in rotateList" :key="item.value" class="menu-item" :class="{'active-item': currentSelectedRect && currentSelectedRect.direction === item.value}" @click.stop="rotateCanvas(item.value)">{{ item.label }}</li>
      </ul>
    </div>
    <div v-else>
      <div class="upload-area">
            <div class="upload-demo">
              <label class="selectBtn" @dragover="fileDragover" @drop="fileDrop">
                <div class="styleOfLabel">
                  <span></span>
                  <p v-if="isExcel">Drag or click to add your file</p>
                  <p v-else style="color: #f56c6c;">Please attach your excel file.</p>
                  <input
                    type="file"
                    accept="application/pdf"
                    class="selectIpt"
                    ref="selectIpt"
                    style="width:1px !important; height: 1px !important;"
                    @change="handleFiles"
                  />
                </div>
              </label>
            </div>
          </div>
    </div>
  </div>
</template>
<script>
import { getTableOutLine, getFileImageList, deleteTableOutLine, uploadFile } from '@/api/file'
// import FileMixin from '../mixins/FileMixin'
export default {
  // components: { pdf },
  // mixins: [FileMixin],
  props: {
    outlineUpdateRes: {
      default: 0,
      type: Number
    }
  },
  data() {
    return {
      pdfImgList: [],
      // 测试数据
      // tableMapList: {
      //   1: [
      //     {
      //       'table_id': 1,
      //       'page': 1,
      //       'x1': 0.2,
      //       'y1': 0.2,
      //       'x2': 0.4,
      //       'y2': 0.4,
      //       'direction': 'up',
      //       'confirmed': false
      //     },
      //     {
      //       'table_id': 2,
      //       'page': 1,
      //       'x1': 0.6,
      //       'y1': 0.6,
      //       'x2': 0.8,
      //       'y2': 0.8,
      //       'direction': 'up',
      //       'confirmed': false
      //     }
      //   ],
      //   2: [
      //     {
      //       'table_id': 3,
      //       'page': 1,
      //       'x1': 0.2,
      //       'y1': 0.2,
      //       'x2': 0.8,
      //       'y2': 0.8,
      //       'direction': 'up',
      //       'confirmed': false
      //     },
      //     {
      //       'table_id': 4,
      //       'page': 1,
      //       'x1': 0.2,
      //       'y1': 0.2,
      //       'x2': 0.8,
      //       'y2': 0.8,
      //       'direction': 'up',
      //       'confirmed': false
      //     }
      //   ]
      // },
      tableMapList: {},
      scale: 1,
      // 当前选择的框线
      currentSelectedRect: null,
      isShowContextMenu: false,
      menuX: 0,
      menuY: 0,
      rotateList: [
        {
          value: 'up',
          label: 'Up(0°)'
        },
        {
          value: 'left',
          label: 'Left(90°)'
        },
        {
          value: 'down',
          label: 'Down(180°)'
        },
        {
          value: 'right',
          label: 'Right(270°)'
        },
        {
          value: 'delete',
          label: 'Delete Tabel'
        }],
      projectId: 0,
      fileId: 0,
      rectColorList: {
        'confirmed': '#2CAC00',
        'confirming': '#D20000',
        'selected': '#003ABF'
      },
      imgLoadLength: 0,
      timer: null,
      keyword: "",
      pdfName: "",
      fileData: {},
      hash: "",
      isExcel: true,
      percent: 0, // 进度条
      pdfCharts: null,
      resultData: {},
      loading: false,
      apiImgObj: {}
    }
  },
  watch: {
    currentSelectedRect(nv, ov) {
      this.$emit('selectTable', {
        tableInfo: nv,
        pageInfo: this.pdfImgList[this.currentIndex]
      })
      this.changeRectColor(nv, ov)
    },
    outlineUpdateRes(nv) {
      // 外框线保存成功
      this.currentSelectedRect.confirmed = true
      this.currentSelectedRect.strokeStyle = this.rectColorList.confirmed
      if (!this.currentSelectedRect.table_id) {
        this.currentSelectedRect.table_id = nv
      }
    }
  },
  mounted() {
    // this.initDomData()
    // this.initDomEvent()
    this.isShowContextMenu = false
    // this.initFileImage()
    // this.initCanvas()
  },
  created() {
    document.addEventListener('click', () => {
      this.isShowContextMenu = false
    })
  },
  methods: {
    handleFiles() {
      const files = this.$refs.selectIpt.files;
      for (let i = 0, len = files.length; i < len; i++) {
        this.showFilePreview(files[i]);
      }
    },
    initFileImage() {
      this.$emit('getLoading', true)
      getFileImageList(this.fileId).then(res => {
        this.pdfImgList = []
        this.apiImgObj = res
        for(let key in res) {
          this.pdfImgList.push({
            id: key,
            url: `http://10.10.10.225:8280/api/v1/file/pdf_img/${res[key]}`
          })
        }
        // this.$nextTick(() => {
        this.initTableData()
        // })
        setTimeout(() => {
          this.$emit('fileImgList', this.pdfImgList)
          this.$emit('getLoading', false)
        }, 4000)
        // this.initTableData()
      })
    },
    initTableData() {
      // this.fileId
      getTableOutLine(JSON.stringify(this.apiImgObj)).then(res => {
        const tableRawList = res
        this.tableMapList = {}
        tableRawList.forEach(item => {
          // 将图片和每页的table对应
          const rowArr = this.tableMapList[item.page] || []
          this.tableMapList[item.page] = rowArr.concat([item])
        })
        this.initCanvas()
        // this.initCanvas()
      }).catch(() => {
        this.tableMapList = {}
      })
    },
    initCanvas() {
      this.imgLoadLength = 0
      this.pdfImgList.forEach((item, index) => {
        item = this.initObjItem(item)
        // const itemTableList = this.tableMapList[item.id]
        // if (itemTableList && itemTableList.length) {
        // init canvas
        this.initDomData(item, index)
        // init outline in canvas
        // }
      })
    },
    initObjItem(obj) {
      const data = {
        currentIndex: 0,
        canvasObj: null,
        canvasCtx: null,
        // 起始x坐标
        startx: 0,
        // 起始y坐标
        starty: 0,
        currentX: 0,
        currentY: 0,
        leftDistance: 0,
        topDistance: 0,
        // 是否点击鼠标的标志
        isMouseDown: false,
        elementWidth: 1180,
        elementHeight: 800,
        // op操作类型 0 无操作 1 画矩形框 2 拖动矩形框
        op: 0,
        // 图层
        layers: [],
        // 当前点击的矩形框
        currentRect: null,
        type: 0
      }
      return Object.assign(data, obj)
    },
    initDomData(item, index) {
      const canvasId = 'canvas-' + item.id
      const imgId = 'pdf-img-' + item.id
      const obj = this.pdfImgList
      const id = item.id
      obj[index]['canvasObj'] = document.getElementById(canvasId)
      obj[index]['canvasCtx'] = obj[index]['canvasObj'].getContext('2d')
      // this.$nextTick(() => {
      const imgDom = document.getElementById(imgId)
      imgDom.onload = () => {
        const width = imgDom.width
        const height = imgDom.height
        obj[index]['canvasObj'].setAttribute('width', width)
        obj[index]['canvasObj'].setAttribute('height', height)
        obj[index]['elementWidth'] = width
        obj[index]['elementHeight'] = height
        this.initItemLayers(index, width, height, id)
        this.initDomEvent(obj[index]['canvasObj'], index)
        ++this.imgLoadLength
        this.$emit('imgLoadLength', this.imgLoadLength)
      }
      imgDom.src = item.url
      // })
      // const scaleStep = 1.05
    },
    initItemLayers(index, width, height, id) {
      const itemTableList = this.tableMapList[id] || []
      const layers = new Array(itemTableList.length)
      itemTableList.forEach((table, index) => {
        const color = table.confirmed ? this.rectColorList.confirmed : this.rectColorList.confirming
        const { x1, x2, y1, y2, direction, table_id, page } = table
        layers[index] = this.initTableOutline(x1 * width, y1 * height, x2 * width, y2 * height, 0, direction, table_id, page, color, table.confirmed)
      })
      this.pdfImgList[index]['layers'] = layers
      this.reshow(0, 0, this.pdfImgList[index])
    },
    initDomEvent(canvasObj, index) {
      canvasObj.onmouseenter = () => {
        canvasObj.onmousedown = (e) => { this.mousedown(e, index) }
        canvasObj.onmousemove = this.mousemove
        document.onmouseup = this.mouseup
      }
      canvasObj.onmouseleave = () => {
        canvasObj.onmousedown = null
        canvasObj.onmousemove = null
        canvasObj.onmouseup = null
      }
      canvasObj.onkeydown = this.keyDown
    },
    // 增大
    // document.querySelector('#up').onclick=function(){
    // 	if(c.width<=maxWidth&&c.height<=maxHeight){
    // 		c.width*=scaleStep;
    // 		c.height*=scaleStep;
    // 		scale=c.height/minHeight;
    // 		ctx.scale(scale,scale)
    // 		c.style.backgroundSize=`${c.width}px ${c.height}px`;
    // 		reshow()
    // 	}
    // }
    // 减小
    // document.querySelector('#down').onclick=function(){
    // 	if(c.width>=minWidth&&c.height>=minHeight){
    // 		c.width/=scaleStep;
    // 		c.height/=scaleStep;
    // 		scale=c.height/minHeight;
    // 		ctx.scale(scale,scale);
    //         c.style.backgroundSize=`${c.width}px ${c.height}px`;
    // 		reshow();
    // 	}
    // }
    // 撤销
    // document.querySelector('#cancel').onclick=function(){
    //     layers.pop();
    // 	ctx.clearRect(0,0,elementWidth,elementHeight);
    //     reshow();
    // }
    // 清空
    // document.querySelector('#clear').onclick=function(){
    //     layers=[];
    // 	ctx.clearRect(0,0,elementWidth,elementHeight);
    //     reshow();
    // }
    updateConfirmed(obj) {
      if (!this.currentSelectedRect && obj && obj.currentRect) {
        this.currentSelectedRect = obj.currentRect
      }
      obj.confirmed = false
      if (this.currentSelectedRect) {
        this.$set(this.currentSelectedRect, 'confirmed', false)
      }
    },
    resizeLeft(rect) {
      const obj = this.pdfImgList[this.currentIndex]
      // this.currentSelectedRect = obj.currentRect
      obj.canvasObj.style.cursor = 'w-resize'
      if (obj.isMouseDown && obj.op === 0) { obj.op = 3 }
      if (obj.isMouseDown && obj.op === 3) {
        if (!obj.currentRect) { obj.currentRect = rect }
        obj.currentRect.x1 = obj.currentX
        obj.currentRect.width = obj.currentRect.x2 - obj.currentRect.x1
      }
      if (obj.isMouseDown && obj.op !== 0) { this.updateConfirmed(obj) }
    },
    resizeTop(rect) {
      const obj = this.pdfImgList[this.currentIndex]
      // this.currentSelectedRect = obj.currentRect
      obj.canvasObj.style.cursor = 's-resize'
      if (obj.isMouseDown && obj.op === 0) { obj.op = 4 }
      if (obj.isMouseDown && obj.op === 4) {
        if (!obj.currentRect) { obj.currentRect = rect }
        obj.currentRect.y1 = obj.currentY
        obj.currentRect.height = obj.currentRect.y2 - obj.currentRect.y1
      }
      if (obj.isMouseDown && obj.op !== 0) { this.updateConfirmed(obj) }
    },
    resizeWidth(rect) {
      const obj = this.pdfImgList[this.currentIndex]
      // this.currentSelectedRect = obj.currentRect
      obj.canvasObj.style.cursor = 'w-resize'
      if (obj.isMouseDown && obj.op === 0) { obj.op = 5 }
      if (obj.isMouseDown && obj.op === 5) {
        if (!obj.currentRect) { obj.currentRect = rect }
        obj.currentRect.x2 = obj.currentX
        obj.currentRect.width = obj.currentRect.x2 - obj.currentRect.x1
      }
      if (obj.isMouseDown && obj.op !== 0) { this.updateConfirmed(obj) }
    },
    resizeHeight(rect) {
      const obj = this.pdfImgList[this.currentIndex]
      // this.currentSelectedRect = obj.currentRect
      obj.canvasObj.style.cursor = 's-resize'
      if (obj.isMouseDown && obj.op === 0) { obj.op = 6 }
      if (obj.isMouseDown && obj.op === 6) {
        if (!obj.currentRect) { obj.currentRect = rect }
        obj.currentRect.y2 = obj.currentY
        obj.currentRect.height = obj.currentRect.y2 - obj.currentRect.y1
      }
      if (obj.isMouseDown && obj.op !== 0) { this.updateConfirmed(obj) }
    },
    resizeLT(rect) {
      const obj = this.pdfImgList[this.currentIndex]
      // this.currentSelectedRect = obj.currentRect
      obj.canvasObj.style.cursor = 'se-resize'
      if (obj.isMouseDown && obj.op === 0) { obj.op = 7 }
      if (obj.isMouseDown && obj.op === 7) {
        if (!obj.currentRect) { obj.currentRect = rect }
        obj.currentRect.x1 = obj.currentX
        obj.currentRect.y1 = obj.currentY
        obj.currentRect.height = obj.currentRect.y2 - obj.currentRect.y1
        obj.currentRect.width = obj.currentRect.x2 - obj.currentRect.x1
      }
      if (obj.isMouseDown && obj.op !== 0) { this.updateConfirmed(obj) }
    },
    resizeWH(rect) {
      const obj = this.pdfImgList[this.currentIndex]
      // this.currentSelectedRect = obj.currentRect
      obj.canvasObj.style.cursor = 'se-resize'
      if (obj.isMouseDown && obj.op === 0) { obj.op = 8 }
      if (obj.isMouseDown && obj.op === 8) {
        if (!obj.currentRect) { obj.currentRect = rect }
        obj.currentRect.x2 = obj.currentX
        obj.currentRect.y2 = obj.currentY
        obj.currentRect.height = obj.currentRect.y2 - obj.currentRect.y1
        obj.currentRect.width = obj.currentRect.x2 - obj.currentRect.x1
      }
      if (obj.isMouseDown && obj.op !== 0) { this.updateConfirmed(obj) }
    },
    resizeLH(rect) {
      const obj = this.pdfImgList[this.currentIndex]
      // this.currentSelectedRect = obj.currentRect
      obj.canvasObj.style.cursor = 'ne-resize'
      if (obj.isMouseDown && obj.op === 0) { obj.op = 9 }
      if (obj.isMouseDown && obj.op === 9) {
        if (!obj.currentRect) { obj.currentRect = rect }
        obj.currentRect.x1 = obj.currentX
        obj.currentRect.y2 = obj.currentY
        obj.currentRect.height = obj.currentRect.y2 - obj.currentRect.y1
        obj.currentRect.width = obj.currentRect.x2 - obj.currentRect.x1
      }
      if (obj.isMouseDown && obj.op !== 0) { this.updateConfirmed(obj) }
    },
    resizeWT(rect) {
      const obj = this.pdfImgList[this.currentIndex]
      // this.currentSelectedRect = obj.currentRect
      obj.canvasObj.style.cursor = 'ne-resize'
      if (obj.isMouseDown && obj.op === 0) { obj.op = 10 }
      if (obj.isMouseDown && obj.op === 10) {
        if (!obj.currentRect) { obj.currentRect = rect }
        obj.currentRect.x2 = obj.currentX
        obj.currentRect.y1 = obj.currentY
        obj.currentRect.height = obj.currentRect.y2 - obj.currentRect.y1
        obj.currentRect.width = obj.currentRect.x2 - obj.currentRect.x1
      }
      if (obj.isMouseDown && obj.op !== 0) { this.updateConfirmed(obj) }
    },
    // 删除框线
    deleteRect(index) {
      const obj = this.pdfImgList[index]
      if (obj && this.currentSelectedRect && obj.layers) {
        // 获取当前点击框线，将框线从layers中删除
        const layerIndex = obj.layers.findIndex(item => {
          const { height, width, x1, x2, y1, y2, type } = this.currentSelectedRect
          return (item.height === height && item.width === width && item.x1 === x1 && item.x2 === x2 && item.y1 === y1 && item.y2 === y2 && item.type === type)
        })
        if (layerIndex === -1) {
          return
        }
        obj.layers.splice(layerIndex, 1)
        // 清除框线
        obj.canvasCtx.clearRect(0, 0, obj.elementWidth, obj.elementHeight)
        // 重新渲染
        this.reshow(0, 0, obj)
      }
    },
    // 旋转
    rotateRect(direction) {
      // 暂时不做框线视图改变
      // const angleMap = {
      //   'up': 0,
      //   'down': 180,
      //   'left': 90,
      //   'right': 270
      // }
      const obj = this.pdfImgList[this.currentIndex]
      if (obj && this.currentSelectedRect && obj.layers) {
        const layerIndex = obj.layers.findIndex(item => {
          const { height, width, x1, x2, y1, y2, type } = this.currentSelectedRect
          return (item.height === height && item.width === width && item.x1 === x1 && item.x2 === x2 && item.y1 === y1 && item.y2 === y2 && item.type === type)
        })
        if (layerIndex === -1) {
          return
        }
        if (obj.layers[layerIndex].direction === direction) {
          return
        }
        // const layer = obj.layers[layerIndex]
        // // 计算矩形中心点
        // const width = layer.width
        // const height = layer.height
        // const rectCenterPoint = { x: layer.x1 + width / 2, y: layer.y1 + height / 2 }
        // const newPointMap = {
        //   0: {},
        //   1: {
        //     x1: rectCenterPoint.x - width / 2,
        //     x2: rectCenterPoint.x + width / 2,
        //     y1: rectCenterPoint.y - height / 2,
        //     y2: rectCenterPoint.y + height / 2,
        //     height: width,
        //     width: height
        //   }
        // }
        // const angle = Math.abs(angleMap[position] - angleMap[layer.direction])
        // const oddOrEven = (angle / 90) % 2
        // const newLayer = Object.assign(layer, newPointMap[oddOrEven] || {}, { direction: position })
        // obj.layers[layerIndex] = newLayer
        // // 清除框线
        // obj.canvasCtx.clearRect(0, 0, obj.elementWidth, obj.elementHeight)
        // // 重新渲染
        // this.reshow(0, 0, obj)
        obj.layers[layerIndex].direction = direction
        this.updateConfirmed(obj)
      }
    },
    reshow(x, y, obj) {
      let allNotIn = 1
      if (!obj.layers) {
        return
      }
      obj.layers.forEach(item => {
        obj.canvasCtx.beginPath()
        obj.canvasCtx.rect(item.x1, item.y1, item.width, item.height)
        obj.canvasCtx.strokeStyle = item.strokeStyle
        if (x >= (item.x1 - 15 / this.scale) && x <= (item.x1 + 15 / this.scale) && y <= (item.y2 - 15 / this.scale) && y >= (item.y1 + 15 / this.scale)) {
          this.resizeLeft(item)
        } else if (x >= (item.x2 - 15 / this.scale) && x <= (item.x2 + 15 / this.scale) && y <= (item.y2 - 15 / this.scale) && y >= (item.y1 + 15 / this.scale)) {
          this.resizeWidth(item)
        } else if (y >= (item.y1 - 15 / this.scale) && y <= (item.y1 + 15 / this.scale) && x <= (item.x2 - 15 / this.scale) && x >= (item.x1 + 15 / this.scale)) {
          this.resizeTop(item)
        } else if (y >= (item.y2 - 15 / this.scale) && y <= (item.y2 + 15 / this.scale) && x <= (item.x2 - 15 / this.scale) && x >= (item.x1 + 15 / this.scale)) {
          this.resizeHeight(item)
        } else if (x >= (item.x1 - 15 / this.scale) && x <= (item.x1 + 15 / this.scale) && y <= (item.y1 + 15 / this.scale) && y >= (item.y1 - 15 / this.scale)) {
          this.resizeLT(item)
        } else if (x >= (item.x2 - 15 / this.scale) && x <= (item.x2 + 15 / this.scale) && y <= (item.y2 + 15 / this.scale) && y >= (item.y2 - 15 / this.scale)) {
          this.resizeWH(item)
        } else if (x >= (item.x1 - 15 / this.scale) && x <= (item.x1 + 15 / this.scale) && y <= (item.y2 + 15 / this.scale) && y >= (item.y2 - 15 / this.scale)) {
          this.resizeLH(item)
        } else if (x >= (item.x2 - 15 / this.scale) && x <= (item.x2 + 15 / this.scale) && y <= (item.y1 + 15 / this.scale) && y >= (item.y1 - 15 / this.scale)) {
          this.resizeWT(item)
        }
        if (obj.canvasCtx.isPointInPath(x * this.scale, y * this.scale)) {
          this.render(item)
          allNotIn = 0
        }
        obj.canvasCtx.stroke()
      })
      if (obj.isMouseDown && allNotIn && obj.op < 3) {
        obj.op = 1
      }
    },
    render(rect) {
      const obj = this.pdfImgList[this.currentIndex]
      obj.canvasObj.style.cursor = 'move'
      if (obj.isMouseDown && obj.op === 0) { obj.op = 2 }
      if (obj.isMouseDown && obj.op === 2) {
        if (!obj.currentRect) { obj.currentRect = rect }
        obj.currentRect.x2 += obj.currentX - obj.leftDistance - obj.currentRect.x1
        obj.currentRect.x1 += obj.currentX - obj.leftDistance - obj.currentRect.x1
        obj.currentRect.y2 += obj.currentY - obj.topDistance - obj.currentRect.y1
        obj.currentRect.y1 += obj.currentY - obj.topDistance - obj.currentRect.y1
      }
    },
    isPointInRetc(x, y) {
      const obj = this.pdfImgList[this.currentIndex]
      const len = obj.layers.length
      for (let i = 0; i < len; i++) {
        if (obj.layers[i].x1 < x && x < obj.layers[i].x2 && obj.layers[i].y1 < y && y < obj.layers[i].y2) {
          return obj.layers[i]
        }
      }
    },
    fixPosition(position) {
      if (position.x1 > position.x2) {
        const x = position.x1
        position.x1 = position.x2
        position.x2 = x
      }
      if (position.y1 > position.y2) {
        const y = position.y1
        position.y1 = position.y2
        position.y2 = y
      }
      position.width = position.x2 - position.x1
      position.height = position.y2 - position.y1
      // if (position.width < 50 || position.height < 50) {
      //   position.width = 60
      //   position.height = 60
      //   position.x2 += position.x1 + 60
      //   position.y2 += position.y1 + 60
      // }
      return position
    },
    changeRectColor(nv, ov) {
      if (nv) {
        const newLayer = Object.assign(nv, {})
        const currentObj = this.pdfImgList.find(item => item.id === newLayer.page)
        if (currentObj) {
          const index = currentObj.layers.findIndex(item => item.table_id === newLayer.table_id)
          if (index !== -1) {
            currentObj.layers[index].strokeStyle = this.rectColorList.selected
            currentObj.canvasCtx.clearRect(0, 0, currentObj.elementWidth, currentObj.elementHeight)
            // 重新渲染
            this.reshow(0, 0, currentObj)
          }
        }
      }
      if (ov) {
        const oldLayer = Object.assign(ov, {})
        const oldObj = this.pdfImgList.find(item => item.id === oldLayer.page)
        if (oldObj) {
          const index = oldObj.layers.findIndex(item => item.table_id === oldLayer.table_id)
          if (index !== -1) {
            oldObj.layers[index].strokeStyle = ov.confirmed ? this.rectColorList.confirmed : this.rectColorList.confirming
            oldObj.canvasCtx.clearRect(0, 0, oldObj.elementWidth, oldObj.elementHeight)
            // 重新渲染
            this.reshow(0, 0, oldObj)
          }
        }
      }
    },
    mousedown(e, index) {
      this.currentIndex = index
      const obj = this.pdfImgList[this.currentIndex]
      // 初始化颜色
      // this.initRectColor(obj)
      // this.startx = (e.pageX - this.canvasObj.offsetLeft + this.canvasObj.parentElement.scrollLeft) / this.scale
      // this.starty = (e.pageY - this.canvasObj.offsetTop + this.canvasObj.parentElement.scrollTop) / this.scale
      obj.startx = e.offsetX
      obj.starty = e.offsetY
      obj.currentRect = this.isPointInRetc(obj.startx, obj.starty)
      if (obj.currentRect) {
        obj.leftDistance = obj.startx - obj.currentRect.x1
        obj.topDistance = obj.starty - obj.currentRect.y1
        // obj.currentRect.strokeStyle = this.rectColorList.selected
      }
      obj.canvasCtx.strokeRect(obj.currentX, obj.currentY, 0, 0)
      // obj.canvasCtx.strokeStyle = this.rectColorList.selected
      obj.isMouseDown = 1
      this.currentSelectedRect = obj.currentRect
    },
    mousemove(e) {
      const obj = this.pdfImgList[this.currentIndex]
      if (obj) {
        // this.currentX = (e.pageX - this.canvasObj.offsetLeft + this.canvasObj.parentElement.scrollLeft) / this.scale
      // this.currentY = (e.pageY - this.canvasObj.offsetTop + this.canvasObj.parentElement.scrollTop) / this.scale
        obj.currentX = e.offsetX
        obj.currentY = e.offsetY
        obj.canvasCtx.save()
        obj.canvasCtx.setLineDash([5])
        obj.canvasObj.style.cursor = 'default'
        obj.canvasCtx.clearRect(0, 0, obj.elementWidth, obj.elementHeight)
        if (obj.isMouseDown && obj.op === 1) {
          if ((obj.currentX - obj.startx > 30) || (obj.currentY - obj.starty > 30)) {
            // 移动幅度太小，不画框
            obj.canvasCtx.strokeRect(obj.startx, obj.starty, obj.currentX - obj.startx, obj.currentY - obj.starty)
          }
        }
        obj.canvasCtx.restore()
        this.reshow(obj.currentX, obj.currentY, obj)
      }
    },
    mouseup() {
      const obj = this.pdfImgList[this.currentIndex]
      if (!obj) return
      if (obj.op === 1) {
        // 添加画框
        const x1 = obj.startx
        const y1 = obj.starty
        const x2 = obj.currentX
        const y2 = obj.currentY
        if ((x2 - x1 > 30) || (y2 - y1 > 30)) {
          // 移动幅度太小，不画框
          // 画矩形框
          const layer = this.fixPosition({
            x1,
            y1,
            x2,
            y2,
            strokeStyle: this.rectColorList.selected,
            type: obj.type || 0,
            direction: 'up',
            table_id: 0,
            page: obj.id
          })
          obj.layers.push(layer)
          this.currentSelectedRect = layer
        }
      } else if (obj.op >= 3) {
        // 改变框线长宽
        this.currentSelectedRect = obj.currentRect
        this.fixPosition(obj.currentRect)
      } else if (obj.op === 2) {
        // 移动框线
        this.updateConfirmed(obj)
      }
      obj.currentRect = null
      obj.isMouseDown = 0
      this.reshow(obj.currentX, obj.currentY, obj)
      obj.op = 0
      // this.currentIndex = 0
    },
    keyDown() {
      // if (e.keyCode === 8) {
      //   // 删除框线
      //   this.confirmDelete(index)
      // }
    },
    initTableOutline(x1, y1, x2, y2, type, direction, table_id, page, strokeStyle, confirmed) {
      const layer = this.fixPosition({
        x1,
        y1,
        x2,
        y2,
        strokeStyle,
        type,
        direction,
        table_id,
        page,
        confirmed
      })
      return layer
    },
    showContextMenu(event) {
      if (this.currentSelectedRect) {
        this.isShowContextMenu = true
        this.menuX = event.clientX
        this.menuY = event.clientY
      }
    },
    rotateCanvas(value) {
      if (value === 'delete') {
        this.confirmDelete(this.currentIndex)
      } else {
        this.rotateRect(value)
      }
      this.isShowContextMenu = false
    },
    deleteOutline(index) {
      const obj = this.pdfImgList[index]
      if (obj && this.currentSelectedRect && obj.layers) {
        const params = {
          table_ids: this.currentSelectedRect.table_id
        }
        deleteTableOutLine(this.projectId, this.fileId, params).then(() => {
          this.deleteRect(index)
        }).catch(() => {
          this.$notify.error({
            title: 'Error',
            message: 'Error, Please try again!'
          })
        })
      }
    },
    confirmDelete(index) {
      // table_id为0时直接删除框线
      if (!this.currentSelectedRect.table_id) {
        this.deleteRect(index)
        return
      }
      this.$confirm(`Please confirm that you will delete this outline.`, 'Warning', {
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }).then(() => {
        this.deleteRect(index)
        // 不调用接口
        // this.deleteOutline(index)
      })
    },
    fileDragover(e) {
      e.preventDefault();
    },
    fileDrop(e) {
      e.preventDefault();
      const file = e.dataTransfer.files[0]; // 获取到第一个上传的文件对象
      if (!file) return;
      this.fileData = file;
      this.pdfName = file.name;
      // const URL = window.URL || window.webkitURL;
      // let pdfUrl = URL.createObjectURL(file);
      // let embedNode = document.createElement("embed");
      // embedNode.src = pdfUrl;
      // embedNode.setAttribute("height", "500px");
      // embedNode.setAttribute("width", "100%");
      // let newLi = document.createElement("li");
      // newLi.appendChild(embedNode);
      // this.$refs.previewList.appendChild(newLi);
      this.postForm();
    },
    showFilePreview(file) {
      const fileType = file.type;
      if (!fileType) {
        this.isExcel = false
        return;
      }
      const fileTypeList = ['application/pdf']
      if (fileTypeList.includes(fileType)) {
        this.isExcel = true
        return this.handlePdfFile(file);
      } else {
        this.isExcel = false
      }
    },
    handlePdfFile(file) {
      // 使用URL来处理
      this.fileData = file;
      const URL = window.URL || window.webkitURL;
      let pdfUrl = URL.createObjectURL(file);
      this.pdfName = file.name || "EXCEL";
      let embedNode = document.createElement("embed");
      embedNode.src = pdfUrl;
      embedNode.setAttribute("height", "500px");
      embedNode.setAttribute("width", "100%");
      embedNode.setAttribute("z-index", "3");
      this.createPreviewItem(embedNode);
    },
    createPreviewItem() {
      // let newLi = document.createElement("li");
      // newLi.appendChild(newNode);
      // this.$refs.previewList.appendChild(newLi);
      this.postForm();
    },
    postForm() {
      this.timer = setInterval(() => {
        if (this.percent < 99) {
          this.percent++;
        } else {
          clearInterval(this.timer);
        }
      }, 600);
      let fd = new FormData();
      fd.append("file", this.fileData);
      uploadFile(fd).then(res => {
        this.fileId = res.file_hash
        this.$emit('fileId', this.fileId)
        this.initFileImage()
      })
      // let config = {
      //   headers: {
      //     "Content-Type": "multipart/form-data"
      //   },
      //   "reloadOnError": true,
      // };
      // ajaxUploadPdf(fd, config)
      //   .then(res => {
      //     this.percent = 100;
      //     this.hash = res.data.md5;
      //     // const { AC, RD, GR, RS, KTH, DEN, CNL, CAL } = res.data['return data']
      //     this.resultData = res.data['return data']
      //     setTimeout(() => {
      //       this.percent = 0;
      //       clearInterval(this.timer);
      //     }, 500);
      //   })
      //   .finally(() => {
      //     this.percent = -10000;
      //   });
    }
  }
}
</script>
<style lang="less" scoped>
// embed {
//     -webkit-transform: translate(30px, -50px);
//     transform: translate(30px, -50px);
//     width: 100%;
//     height: 100%;
// }
.pdf-img-box {
  font-size: 0;
  position: relative;
  clear: both;
  overflow: hidden;
  .pdf-img {
    clear: both;
    overflow: hidden;
  }
  .img-canvas {
    position: absolute;
    top: 0;
    left: 0;
    z-index: 2;
    height: 100%;
    width: 100%;
  }
}
.pdf-img {
  width: 100%;
}
.upload-area {
  width: 100%;
  height: 150px;
  border-radius: 4px;
  background: rgba(247, 248, 250, 1);
  .upload-demo {
    position: relative;
    width: 100%;
    height: 100%;
    .selectBtn {
      width: 100%;
      height: 100%;
      display: flex;
      justify-content: center;
      align-items: center;
      .styleOfLabel {
        cursor: pointer;
        margin-top: 12px;
        span {
          margin: 0 auto 5px;
          width: 96px;
          height: 96px;
          display: block;
          background: url("../images/icon-upload.png") no-repeat center
            center;
          background-size: 100%;
        }
        p {
          color: #777777;
          font-size: 15px;
        }
      }
    }
    .previewBox {
      width: 210px;
      height: 150px;
      z-index: 1;
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: rgba(247, 248, 250, 1);
      .closed {
        z-index: 3;
        width: 25px;
        height: 25px;
        line-height: 25px;
        text-align: center;
        color: #ffffff;
        background: #83a7cf;
        border-radius: 100px;
        position: absolute;
        top: calc(50% - 45px);
        left: 200px;
      }
      .previewList {
        z-index: 2;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 100%;
        height: 100%;
        overflow: hidden;
        .pdfName {
          padding: 5px;
          box-sizing: border-box;
          z-index: 4;
          position: absolute;
          top: calc(50% - 30px);
          left: 50%;
          transform: translate(-50%, 0);
          width: 100%;
          height: 58px;
          display: flex;
          align-items: center;
          color: #ffffff;
          font-size: 14px;
          background: gray;
          overflow: hidden;
        }
      }
    }
  }
}
.context-menu {
  position: fixed;
  z-index:2000;
  padding: 6px 0;
  background: #fff;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
  border-radius: 4px;
  border: 1px solid #e6ebf5;
  .menu-item {
    padding: 8px 20px;
    width: 150px;
    text-align: center;
    font-size: 14px;
    &:hover {
      background: #eee;
      cursor: pointer;
    }
    &.active-item {
      color: #007cc4;
      font-weight: 500;
    }
  }
}
</style>
