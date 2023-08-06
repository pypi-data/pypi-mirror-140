

def guardar_captura(driver, captura_error):
    try:
        if driver is not None:
            driver.save_screenshot(captura_error)
    except:
        pass


def close_driver(driver):
    try:
        if driver is not None:
            driver.quit()
    except:
        pass



