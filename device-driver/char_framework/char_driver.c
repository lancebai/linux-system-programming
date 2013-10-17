#include <linux/module.h>
#include <linux/version.h>
#include <linux/kernel.h>

#include <linux/types.h>
#include <linux/kdev_t.h>
#include <linux/fs.h>

static dev_t char_driver_framework;

static int __init char_driver_framwork_init(void) /* Constructor */
{
  printk(KERN_INFO "init: char_driver_framework registered");
  if (alloc_chrdev_region(&char_driver_framework, 0, 3, "Lance") < 0) {
    return -1;
  }
  printk(KERN_INFO "<Major, Minor> : <%d, %d> \n", MAJOR(char_driver_framework), \
         MINOR(char_driver_framework));
  return 0;
}
 
static void __exit char_driver_framwork_exit(void) /* Destructor */
{
  unregister_chrdev_region(char_driver_framework, 3);
  printk(KERN_INFO "exit: char_driver_framework unregistered");
}
 
module_init(char_driver_framwork_init);
module_exit(char_driver_framwork_exit);
 
MODULE_LICENSE("GPL");
MODULE_AUTHOR("Lance Bai <lancebai@gmail.com>");
MODULE_DESCRIPTION("Our First Driver");

