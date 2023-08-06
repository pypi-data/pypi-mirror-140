def disable_widget(widgets):
    for widget in widgets:
        widget.setEnabled(False)   

def enable_widget(widgets):
    for widget in widgets:
        widget.setEnabled(True)  

def convert_fraction_to_float(fraction):
    #code adapted from https://stackoverflow.com/questions/1806278/convert-fraction-to-float
    try:
        return float(fraction)
    except ValueError:
        num, denom = fraction.split('/')
        try:
            leading, num = num.split(' ')
            whole = float(leading)
        except ValueError:
            whole = 0
        frac = float(num) / float(denom)
        return whole - frac if whole < 0 else whole + frac
