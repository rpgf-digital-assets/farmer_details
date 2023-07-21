<script>

    $(document).ready(function() {
        $('#id_{{wizard_current_step}}-TOTAL_FORMS').on('change', function() {
            $('.datetimepicker-input').daterangepicker({
                singleDatePicker: true,
                showDropdowns: true,
                minYear: 1901,
                locale: {
                    format: 'YYYY-MM-DD'
                },
                maxYear: parseInt(moment().format("YYYY"),12)
            });
        })
    
    })
    
</script>