<template>
    <div class="header">
        <div class="layout-left">
            <h1 class="title">Table Extraction</h1>
        </div>
    </div>
</template>
<script>
export default {
    data() {
        return {}
    }
}
</script>
<style lang="less" scoped>
    .header {
        height: 64px;
        background:rgba(0,0,0,0.85);
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 24px;
        color: #fff;
        .layout-right {
            display: flex;
            align-items: center;
        }
        .title {
            font-family: Source Han Sans SC;
            font-weight: 900;
            font-size: 28px;
            margin-left: 16px;
            vertical-align: bottom;
        }
        .link {
            margin-left: 36px;
            cursor: pointer;
        }
        .highlight {
            font-weight: 900;
        }
        .hidden-logo {
            visibility: hidden;
        }
        .link a, .router-link-active {
            color: inherit;
            text-decoration: none;
        }
        
    }
    .dark-style {
        color: #000;
        background: transparent;
    }
</style>