
                
    def led_flash_on(self, mgr_name):
        self.led_dynamic_op(mgr_name, 'led_blink_on')
    
    def led_flash_off(self, mgr_name):
       self.led_dynamic_op(mgr_name, 'led_blink_off')
    
    def led_blink_on(self, mgr_name):
        self.led_dynamic_op(mgr_name, 'led_blink_on')
    
    def led_blink_off(self, mgr_name):
       self.led_dynamic_op(mgr_name, 'led_blink_off')
    
    def led_on(self, mgr_name):
        self.led_dynamic_op(mgr_name, 'led_on')
    
    def led_off(self, mgr_name):
        self.led_dynamic_op(mgr_name, 'led_off')
        
    def led_stop(self, mgr_name):
        self.led_dynamic_op(mgr_name, 'led_stop')
     
    def led_dynamic_op(self, mgr_name, op):   
        if self.active_led_managers == None:
            return;
        
        mgr_thread = self.active_led_managers[mgr_name]
        
        if mgr_thread == None:
            return
        
        try:
            getattr(mgr_thread, op)()
        except Exception as e:
            print(f"Failed to execute {mgr_name}.{op}: {e}") 