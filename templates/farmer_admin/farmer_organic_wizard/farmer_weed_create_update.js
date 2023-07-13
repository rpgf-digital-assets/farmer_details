
<script>
    $("#id_4-date_of_activity").daterangepicker({
        singleDatePicker: true,
        showDropdowns: true,
        minYear: 1901,
        locale: {
            format: 'YYYY-MM-DD'
        },
        maxYear: parseInt(moment().format("YYYY"),12)
    });
</script>