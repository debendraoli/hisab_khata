(function ($) {

	'use strict';

	// ------------------------------------------------------- //
	// Auto Hide
	// ------------------------------------------------------ //	

	$(function () {
		$('#product-table').DataTable({
        "processing": true,
        "serverSide": true,
        "ajax": "",
        "columns": [
            { "data": "" },
            { "data": "" },
            { "data": "" },
            { "data": "" },
            { "data": "" },
            { "data": "" }
        ],
			"lengthMenu": [
				[10, 15, 20, -1],
				[10, 15, 20, "All"]
			],
			"order": [
				[3, "desc"]
			]
		});
	});

	$(function () {
		$('#export-table').DataTable({
			dom: 'Bfrtip',
			buttons: {
				buttons: [{
					extend: 'copy',
					text: 'Copy',
					title: $('h1').text(),
					exportOptions: {
						columns: ':not(.no-print)'
					},
					footer: true
				},{
					extend: 'excel',
					text: 'Excel',
					title: $('h1').text(),
					exportOptions: {
						columns: ':not(.no-print)'
					},
					footer: true
				},{
					extend: 'csv',
					text: 'Csv',
					title: $('h1').text(),
					exportOptions: {
						columns: ':not(.no-print)'
					},
					footer: true
				},{
					extend: 'pdf',
					text: 'Pdf',
					title: $('h1').text(),
					exportOptions: {
						columns: ':not(.no-print)'
					},
					footer: true
				},{
					extend: 'print',
					text: 'Print',
					title: $('h1').text(),
					exportOptions: {
						columns: ':not(.no-print)'
					},
					footer: true,
					autoPrint: true
				}],
				dom: {
					container: {
						className: 'dt-buttons'
					},
					button: {
						className: 'btn btn-primary'
					}
				}
			}
		});
	});

})(jQuery);
