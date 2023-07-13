<script>
    $("#id_5-first_harvest_date").daterangepicker({
        singleDatePicker: true,
        showDropdowns: true,
        minYear: 1901,
        locale: {
            format: 'YYYY-MM-DD'
        },
        maxYear: parseInt(moment().format("YYYY"),12)
    });
    $("#id_5-second_harvest_date").daterangepicker({
        singleDatePicker: true,
        showDropdowns: true,
        minYear: 1901,
        locale: {
            format: 'YYYY-MM-DD'
        },
        maxYear: parseInt(moment().format("YYYY"),12)
    });
    $("#id_5-third_harvest_date").daterangepicker({
        singleDatePicker: true,
        showDropdowns: true,
        minYear: 1901,
        locale: {
            format: 'YYYY-MM-DD'
        },
        maxYear: parseInt(moment().format("YYYY"),12)
    });
    

</script>