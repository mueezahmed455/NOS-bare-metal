#ifndef FILESYSTEM_H
#define FILESYSTEM_H

#include <cstdint>
#include <cstddef>
#include "kernel.h"

// File system constants
#define MAX_FILENAME_LENGTH 256
#define MAX_PATH_LENGTH 1024
#define BLOCK_SIZE 4096
#define MAX_BLOCKS 65536

// File types
enum class FileType {
    REGULAR,
    DIRECTORY,
    SYMLINK,
    DEVICE
};

// File permissions
#define PERM_READ 0x4
#define PERM_WRITE 0x2
#define PERM_EXEC 0x1

// Directory entry
struct DirectoryEntry {
    char name[MAX_FILENAME_LENGTH];
    u32 inode_number;
    FileType type;
};

// Inode structure
struct Inode {
    u32 number;
    FileType type;
    u32 size;
    u32 permissions;
    u32 uid;
    u32 gid;
    u64 atime;
    u64 mtime;
    u64 ctime;
    u32 block_count;
    u32 blocks[12]; // Direct blocks
    u32 indirect_block; // Single indirect
    u32 double_indirect_block; // Double indirect
};

// File descriptor
struct FileDescriptor {
    u32 fd;
    Inode* inode;
    u32 position;
    u32 flags;
};

// File system class
class FileSystem {
public:
    static void initialize();
    static bool mount(const char* device, const char* mount_point);
    static bool unmount(const char* mount_point);

    // File operations
    static i32 open(const char* path, u32 flags);
    static i32 close(u32 fd);
    static isize read(u32 fd, void* buffer, size_t count);
    static isize write(u32 fd, const void* buffer, size_t count);
    static i64 lseek(u32 fd, i64 offset, u32 whence);

    // Directory operations
    static i32 mkdir(const char* path, u32 mode);
    static i32 rmdir(const char* path);
    static i32 readdir(u32 fd, DirectoryEntry* entry);

    // File system operations
    static i32 stat(const char* path, Inode* statbuf);
    static i32 unlink(const char* path);
    static i32 rename(const char* oldpath, const char* newpath);

private:
    static u8* disk_buffer;
    static Inode* inode_table;
    static u32* block_bitmap;
    static u32 total_inodes;
    static u32 total_blocks;
    static u32 free_inodes;
    static u32 free_blocks;

    static u32 allocate_inode();
    static void free_inode(u32 inode_num);
    static u32 allocate_block();
    static void free_block(u32 block_num);
    static Inode* get_inode(u32 inode_num);
    static u32 path_to_inode(const char* path);
    static bool read_block(u32 block_num, void* buffer);
    static bool write_block(u32 block_num, const void* buffer);
};

#endif // FILESYSTEM_H