#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/fs.h>
#include <errno.h>

// COMMAND FLAGS
#define CMD_LOCK "--lock"
#define CMD_SELF_DESTRUCT "--self-destruct"
#define CMD_NEUTRALIZE "--neutralize"

void print_usage(char *prog_name) {
    printf("SCRAM Muscle - Low Level Payload Execution\n");
    printf("Usage: %s <command> <device>\n", prog_name);
    printf("Commands:\n");
    printf("  %s <device>   : Set device to Read-Only (The Shield)\n", CMD_LOCK);
    printf("  %s <device> : WIPE VM HEADERS (The End)\n", CMD_SELF_DESTRUCT);
    printf("  %s <device>    : Neutralize intruder (Stub)\n", CMD_NEUTRALIZE);
}

// THE SHIELD: Hardware Lock + Filesystem Remount
int set_readonly(char *device_path) {
    int ret_val = 0;

    // 1. HARDWARE LOCK (The low-level kernel flag)
    printf("[*] PHASE 1: Applying Hardware Lock on %s...\n", device_path);
    int fd = open(device_path, O_RDONLY);
    if (fd < 0) {
        perror("[!] Error opening device");
        ret_val = 1;
    } else {
        int ro = 1;
        if (ioctl(fd, BLKROSET, &ro) < 0) {
            perror("[!] ioctl BLKROSET failed");
            ret_val = 1;
        } else {
            printf("[+] Hardware Lock ENGAGED.\n");
        }
        close(fd);
    }

    // 2. FILESYSTEM LOCK (The Remount)
    // We execute 'mount -o remount,ro' which forces the driver to stop writing.
    // This works even if we don't know the mount point (Linux is smart).
    printf("[*] PHASE 2: Forcing Filesystem Remount (Read-Only)...\n");
    
    char cmd[512];
    // Construct command: mount -o remount,ro /dev/sdb1
    snprintf(cmd, sizeof(cmd), "mount -o remount,ro %s 2>/dev/null", device_path);
    
    int sys_ret = system(cmd);
    
    if (sys_ret == 0) {
        printf("[+] Filesystem Remounted successfully.\n");
    } else {
        // If it fails, it might not be mounted, which is fine (Hardware lock is enough then)
        printf("[!] Warning: Remount returned non-zero. (Device might not be mounted?)\n");
    }

    return ret_val;
}

// THE END: Wipes the first 10MB of the target drive (For your VM)
int wipe_headers_vm(char *device_path) {
    printf("[!!!] WARNING: INITIATING HEADER WIPE ON %s [!!!]\n", device_path);
    printf("[!!!] THIS IS IRREVERSIBLE.\n");
    
    // Open with O_SYNC to bypass cache and write directly to disk
    int fd = open(device_path, O_WRONLY | O_SYNC);
    if (fd < 0) {
        perror("[!] Failed to open device for wiping");
        return 1;
    }

    // 10MB Buffer of Zeros
    size_t size = 10 * 1024 * 1024; 
    char *buffer = calloc(1, size);
    if (!buffer) {
        perror("[!] Memory allocation failed");
        close(fd);
        return 1;
    }

    ssize_t written = write(fd, buffer, size);
    if (written < 0) {
        perror("[!] Write failed");
    } else {
        printf("[+] FLUSHED: %zd bytes of zeros written to %s.\n", written, device_path);
        printf("[+] Filesystem header is destroyed.\n");
    }

    free(buffer);
    close(fd);
    return (written > 0) ? 0 : 1;
}

// THE STUB: Placeholder for Intruder Neutralization
int neutralize_intruder(char *device_path) {
    printf("[*] STUB: Neutralization protocol called on %s\n", device_path);
    
    // =================================================================
    // [ USER CUSTOMIZATION AREA ]
    // Implement your foreign device wiping logic here.
    // WARNING: Ensure you are targeting the correct device!
    // =================================================================
    
    return 0;
}


// THE QUARANTINE: Remounts /home as Read-Only (Bunker Mode)
// THE QUARANTINE: Remounts /home or forces a Kernel-level Read-Only Lock
int quarantine_home() {
    printf("[*] BUNKER MODE: Quarantining /home...\n");
    
    // Attempt polite remount first
    int ret = system("mount -o remount,ro /home 2>/dev/null");
    
    if (ret == 0) {
        printf("[+] SUCCESS: /home is now READ-ONLY.\n");
        return 0;
    } else {
        printf("[!] /home is busy or not a separate partition.\n");
        printf("[*] Engaging Kernel Emergency Read-Only Lock (SysRq-U)...\n");
        
        // 1. Ensure SysRq is enabled in the kernel
        system("echo 1 > /proc/sys/kernel/sysrq");
        
        // 2. Send the 'u' command: Emergency Remount Read-Only
        system("echo u > /proc/sysrq-trigger");
        
        printf("[+] SUCCESS: Kernel forcefully locked ALL drives to READ-ONLY.\n");
        return 0;
    }
}
int main(int argc, char *argv[]) {
    // 1. We must have at least a command
    if (argc < 2) {
        printf("Usage: %s <command> [device]\n", argv[0]);
        return 1;
    }

    char *command = argv[1];

    // 2. Check commands that DO NOT need a device argument first
    if (strcmp(command, "--quarantine") == 0) {
        return quarantine_home();
    }

    // 3. If it's not quarantine, it MUST have a device argument
    if (argc < 3) {
        printf("Error: This command requires a device target.\n");
        printf("Commands:\n");
        printf("  --lock <device>\n");
        printf("  --self-destruct <device>\n");
        printf("  --neutralize <device>\n");
        printf("  --quarantine\n");
        return 1;
    }

    char *device_path = argv[2];

    // 4. Check commands that DO need a device argument
    if (strcmp(command, "--lock") == 0) {
        return set_readonly(device_path);
    } else if (strcmp(command, "--self-destruct") == 0) {
        return wipe_headers_vm(device_path);
    } else if (strcmp(command, "--neutralize") == 0) {
        return neutralize_intruder(device_path);
    } else {
        printf("[!] Unknown command: %s\n", command);
        return 1;
    }
}