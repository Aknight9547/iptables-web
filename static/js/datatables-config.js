$(document).ready(function() {
    $('#rules-table').DataTable({
        "paging": true,
        "searching": true,
        "ordering": true,
        "info": true,
        "autoWidth": false,
        "language": {
            "lengthMenu": "显示 _MENU_ 条记录",
            "search": "搜索:",
            "paginate": {
                "first": "首页",
                "last": "末页",
                "next": "下一页",
                "previous": "上一页"
            },
            "info": "显示第 _START_ 至 _END_ 条记录，共 _TOTAL_ 条",
            "infoEmpty": "没有可用记录",
            "infoFiltered": "(从 _MAX_ 条记录中筛选)"
        }
    });
    
    $('#history-table').DataTable({
        "paging": true,
        "searching": true,
        "ordering": true,
        "info": true,
        "autoWidth": false,
        "language": {
            "lengthMenu": "显示 _MENU_ 条记录",
            "search": "搜索:",
            "paginate": {
                "first": "首页",
                "last": "末页",
                "next": "下一页",
                "previous": "上一页"
            },
            "info": "显示第 _START_ 至 _END_ 条记录，共 _TOTAL_ 条",
            "infoEmpty": "没有可用记录",
            "infoFiltered": "(从 _MAX_ 条记录中筛选)"
        }
    });
    
    $('#templates-table').DataTable({
        "paging": true,
        "searching": true,
        "ordering": true,
        "info": true,
        "autoWidth": false,
        "language": {
            "lengthMenu": "显示 _MENU_ 条记录",
            "search": "搜索:",
            "paginate": {
                "first": "首页",
                "last": "末页",
                "next": "下一页",
                "previous": "上一页"
            },
            "info": "显示第 _START_ 至 _END_ 条记录，共 _TOTAL_ 条",
            "infoEmpty": "没有可用记录",
            "infoFiltered": "(从 _MAX_ 条记录中筛选)"
        }
    });
    
    $('#recent-history').DataTable({
        "paging": false,
        "searching": false,
        "ordering": false,
        "info": false,
        "autoWidth": false
    });
});