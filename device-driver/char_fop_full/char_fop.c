#include <linux/module.h>
#include <linux/version.h>
#include <linux/kernel.h>
#include <linux/types.h>
#include <linux/kdev_t.h>
#include <linux/fs.h>
#include <linux/device.h>
#include <linux/cdev.h>
#include <linux/uaccess.h>

////macro
#define dbg(format, arg...)  do { printk(KERN_INFO  "%d:%s: " format "\n", __LINE__, __FUNCTION__, ##arg); } while ( 0 )
#define MAX_BUF_LEN 255
////Global variables
static const char sHelloWorld[] = "Hello World!\n\0";
static const ssize_t iStrLen = sizeof(sHelloWorld);

//device number
static dev_t char_driver_framework;

//char device structure
static struct cdev c_dev;

//device class
static struct class *cl;

char message_buf[MAX_BUF_LEN]  = {0};

////Internal functions
static int char_open(struct inode* i, struct file *f)
{
  dbg("char Driver");
  return 0;
}

static int char_close(struct inode* i, struct file *f)
{
  dbg("char Driver");
  return 0;
}

static ssize_t char_read(struct file *f, char __user *buf, size_t len, loff_t *offset)
{
  dbg("device is read at offset %d, read bytes cout = %d", *offset, len);

  //if position is behind the end of a file, then nothing to read
  if(*offset >= iStrLen) {
    return 0;
  }

  //if a user tries to read more than we have, read only as many bytes we have
  if((*offset + len) > iStrLen) {
    dbg("user is trying to read more(%d) than we have(%d)", *offset+len, iStrLen);
    len = iStrLen - *offset;
  }

  dbg("copy %d bytes", len);
  if (copy_to_user((void*)buf, sHelloWorld + *offset , len) != 0) {
    return -EFAULT;
  }

  //move reading position
  *offset += len;
  return len;
}

static ssize_t char_write(struct file *f, char __user *buf, size_t len, loff_t *off)
{
  dbg("enter");
  if (copy_from_user(message_buf, buf , len) != 0) {
    return -EFAULT;
  }
  dbg("%s, len:%d", message_buf, len);
  return len;
}

static struct file_operations char_fops = 
{
  .owner = THIS_MODULE,
  .open = char_open,
  .release = char_close,
  .read = char_read,
  .write = char_write,
};

static int __init char_driver_framwork_init(void) /* Constructor */
{
  dbg( "init: char_driver_framework registered");
  if (alloc_chrdev_region(&char_driver_framework, 0, 1, "Lance") < 0) {
    return -1;
  }

  if((cl = class_create(THIS_MODULE, "chardrv")) == NULL) {
    unregister_chrdev_region(char_driver_framework, 1);
    return -1;
  }

  if(device_create(cl, NULL, char_driver_framework, NULL, "char_fop") == NULL) {
    class_destroy(cl);
    unregister_chrdev_region(char_driver_framework, 1);
    return -1;
  }
  
  cdev_init(&c_dev, &char_fops);

  if(cdev_add(&c_dev, char_driver_framework, 1)== -1) {
    device_destroy(cl, char_driver_framework);
    class_destroy(cl);
    unregister_chrdev_region(char_driver_framework, 1);
    return -1;
  }

  dbg( "<Major, Minor> : <%d, %d>", MAJOR(char_driver_framework), \
         MINOR(char_driver_framework));
  return 0;
}
 
static void __exit char_driver_framwork_exit(void) /* Destructor */
{
  cdev_del(&c_dev);
  device_destroy(cl, char_driver_framework);
  class_destroy(cl);
  unregister_chrdev_region(char_driver_framework, 1);
  dbg( "exit: char_driver_framework unregistered");
}
 
module_init(char_driver_framwork_init);
module_exit(char_driver_framwork_exit);
 
MODULE_LICENSE("GPL");
MODULE_AUTHOR("Lance Bai <lancebai@gmail.com>");
MODULE_DESCRIPTION("Our First Driver");
