/*
    This function is for convert default time in odoo as float, into time data type
    @param  float (21.916944444444443)
    @return time  (21:55:01)
 */
CREATE OR REPLACE FUNCTION float_to_time(hours FLOAT)
        RETURNS TIME AS $$
BEGIN
RETURN MAKE_TIME(
        FLOOR(hours)::INT,  -- hours
        FLOOR((hours - FLOOR(hours)) * 60)::INT,  -- minutes
        ROUND(((hours * 3600)::INT % 60), 0)  -- seconds with casting
       );
END;
    $$ LANGUAGE plpgsql;