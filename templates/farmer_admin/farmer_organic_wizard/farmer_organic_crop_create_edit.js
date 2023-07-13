<script type="text/javascript">
    $("#id_0-date_of_sowing").daterangepicker({
        singleDatePicker: true,
        showDropdowns: true,
        minYear: 1901,
        locale: {
            format: 'YYYY-MM-DD'
        },
        maxYear: parseInt(moment().format("YYYY"),12)
    });
    $("#id_0-expected_date_of_harvesting").daterangepicker({
        singleDatePicker: true,
        showDropdowns: true,
        minYear: 1901,
        locale: {
            format: 'YYYY-MM-DD'
        },
        maxYear: parseInt(moment().format("YYYY"),12)
    });
</script>