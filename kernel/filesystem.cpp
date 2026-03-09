#include "filesystem.h"
#include "kernel.h"
#include "memory.h"

// FileSystem static members
u8* FileSystem::disk_buffer = nullptr;
Inode* FileSystem::inode_table = nullptr;
u32* FileSystem::block_bitmap = nullptr;
u32 FileSystem::total_inodes = 0;
u32 FileSystem::total_blocks = 0;
u32 FileSystem::free_inodes = 0;
u32 FileSystem::free_blocks = 0;

void FileSystem::initialize() {
    // Initialize with 1MB disk buffer for now
    const size_t disk_size = 1024 * 1024;
    disk_buffer = static_cast<u8*>(kmalloc(disk_size));
    if (!disk_buffer) {
        panic("Failed to allocate disk buffer");
    }

    // Initialize structures
    total_inodes = 256;
    total_blocks = (disk_size - total_inodes * sizeof(Inode) - (total_blocks / 32 * sizeof(u32))) / BLOCK_SIZE;

    inode_table = reinterpret_cast<Inode*>(disk_buffer);
    block_bitmap = reinterpret_cast<u32*>(disk_buffer + total_inodes * sizeof(Inode));

    // Initialize inode table and block bitmap
    memset(inode_table, 0, total_inodes * sizeof(Inode));
    memset(block_bitmap, 0, total_blocks / 32 * sizeof(u32));

    free_inodes = total_inodes;
    free_blocks = total_blocks;

    klog(LogLevel::INFO, "File system initialized: %d inodes, %d blocks", total_inodes, total_blocks);
}

bool FileSystem::mount(const char* device, const char* mount_point) {
    // Placeholder - for now just mark as mounted
    klog(LogLevel::INFO, "Mounted device %s at %s", device, mount_point);
    return true;
}

bool FileSystem::unmount(const char* mount_point) {
    klog(LogLevel::INFO, "Unmounted %s", mount_point);
    return true;
}

i32 FileSystem::open(const char* path, u32 flags) {
    u32 inode_num = path_to_inode(path);
    if (inode_num == 0) {
        // File doesn't exist, create if write flag set
        if (flags & 0x1) { // O_CREAT simplified
            inode_num = allocate_inode();
            if (inode_num == 0) return -1;

            Inode* inode = get_inode(inode_num);
            inode->type = FileType::REGULAR;
            inode->size = 0;
            inode->permissions = 0644;
            inode->uid = 0;
            inode->gid = 0;
            inode->atime = inode->mtime = inode->ctime = 0; // TODO: get current time
            inode->block_count = 0;
        } else {
            return -1; // File not found
        }
    }

    // Create file descriptor
    FileDescriptor* fd = static_cast<FileDescriptor*>(kmalloc(sizeof(FileDescriptor)));
    if (!fd) return -1;

    fd->fd = 1; // Simplified - just return 1
    fd->inode = get_inode(inode_num);
    fd->position = 0;
    fd->flags = flags;

    return fd->fd;
}

i32 FileSystem::close(u32 fd) {
    // Simplified - just return success
    return 0;
}

isize FileSystem::read(u32 fd, void* buffer, size_t count) {
    // Simplified implementation
    FileDescriptor* file_fd = reinterpret_cast<FileDescriptor*>(fd); // Simplified cast
    if (!file_fd || !file_fd->inode) return -1;

    Inode* inode = file_fd->inode;
    if (file_fd->position >= inode->size) return 0;

    size_t to_read = count;
    if (file_fd->position + to_read > inode->size) {
        to_read = inode->size - file_fd->position;
    }

    // Read from blocks (simplified - assume contiguous for now)
    if (inode->block_count > 0) {
        u32 block_num = inode->blocks[0];
        u8* block_data = disk_buffer + total_inodes * sizeof(Inode) + (total_blocks / 32 * sizeof(u32)) + block_num * BLOCK_SIZE;
        memcpy(buffer, block_data + file_fd->position, to_read);
    }

    file_fd->position += to_read;
    return to_read;
}

isize FileSystem::write(u32 fd, const void* buffer, size_t count) {
    // Simplified implementation
    FileDescriptor* file_fd = reinterpret_cast<FileDescriptor*>(fd);
    if (!file_fd || !file_fd->inode) return -1;

    Inode* inode = file_fd->inode;

    // Allocate blocks if needed
    if (inode->block_count == 0) {
        u32 block_num = allocate_block();
        if (block_num == 0) return -1;
        inode->blocks[0] = block_num;
        inode->block_count = 1;
    }

    u32 block_num = inode->blocks[0];
    u8* block_data = disk_buffer + total_inodes * sizeof(Inode) + (total_blocks / 32 * sizeof(u32)) + block_num * BLOCK_SIZE;

    size_t to_write = count;
    if (file_fd->position + to_write > BLOCK_SIZE) {
        to_write = BLOCK_SIZE - file_fd->position;
    }

    memcpy(block_data + file_fd->position, buffer, to_write);
    file_fd->position += to_write;

    if (file_fd->position > inode->size) {
        inode->size = file_fd->position;
    }

    return to_write;
}

i64 FileSystem::lseek(u32 fd, i64 offset, u32 whence) {
    FileDescriptor* file_fd = reinterpret_cast<FileDescriptor*>(fd);
    if (!file_fd) return -1;

    switch (whence) {
        case 0: // SEEK_SET
            file_fd->position = offset;
            break;
        case 1: // SEEK_CUR
            file_fd->position += offset;
            break;
        case 2: // SEEK_END
            file_fd->position = file_fd->inode->size + offset;
            break;
    }

    return file_fd->position;
}

i32 FileSystem::mkdir(const char* path, u32 mode) {
    u32 inode_num = allocate_inode();
    if (inode_num == 0) return -1;

    Inode* inode = get_inode(inode_num);
    inode->type = FileType::DIRECTORY;
    inode->size = 0;
    inode->permissions = mode | 0x1000; // Directory flag
    inode->uid = 0;
    inode->gid = 0;
    inode->atime = inode->mtime = inode->ctime = 0;
    inode->block_count = 0;

    return 0;
}

i32 FileSystem::rmdir(const char* path) {
    u32 inode_num = path_to_inode(path);
    if (inode_num == 0) return -1;

    Inode* inode = get_inode(inode_num);
    if (inode->type != FileType::DIRECTORY) return -1;

    free_inode(inode_num);
    return 0;
}

i32 FileSystem::readdir(u32 fd, DirectoryEntry* entry) {
    // Simplified - not implemented
    return -1;
}

i32 FileSystem::stat(const char* path, Inode* statbuf) {
    u32 inode_num = path_to_inode(path);
    if (inode_num == 0) return -1;

    *statbuf = *get_inode(inode_num);
    return 0;
}

i32 FileSystem::unlink(const char* path) {
    u32 inode_num = path_to_inode(path);
    if (inode_num == 0) return -1;

    free_inode(inode_num);
    return 0;
}

i32 FileSystem::rename(const char* oldpath, const char* newpath) {
    // Simplified - not implemented
    return -1;
}

u32 FileSystem::allocate_inode() {
    if (free_inodes == 0) return 0;

    for (u32 i = 1; i < total_inodes; i++) {
        if (inode_table[i].type == FileType::REGULAR && inode_table[i].size == 0) {
            free_inodes--;
            return i;
        }
    }
    return 0;
}

void FileSystem::free_inode(u32 inode_num) {
    if (inode_num >= total_inodes) return;

    Inode* inode = &inode_table[inode_num];
    memset(inode, 0, sizeof(Inode));
    free_inodes++;
}

u32 FileSystem::allocate_block() {
    if (free_blocks == 0) return 0;

    for (u32 i = 0; i < total_blocks; i++) {
        u32 bitmap_index = i / 32;
        u32 bit_index = i % 32;

        if (!(block_bitmap[bitmap_index] & (1 << bit_index))) {
            block_bitmap[bitmap_index] |= (1 << bit_index);
            free_blocks--;
            return i;
        }
    }
    return 0;
}

void FileSystem::free_block(u32 block_num) {
    if (block_num >= total_blocks) return;

    u32 bitmap_index = block_num / 32;
    u32 bit_index = block_num % 32;

    block_bitmap[bitmap_index] &= ~(1 << bit_index);
    free_blocks++;
}

Inode* FileSystem::get_inode(u32 inode_num) {
    if (inode_num >= total_inodes) return nullptr;
    return &inode_table[inode_num];
}

u32 FileSystem::path_to_inode(const char* path) {
    // Simplified - assume root directory and direct filename
    if (strcmp(path, "/") == 0) return 1; // Root inode

    // For now, just return inode 2 for any file
    return 2;
}

bool FileSystem::read_block(u32 block_num, void* buffer) {
    if (block_num >= total_blocks) return false;

    u8* block_data = disk_buffer + total_inodes * sizeof(Inode) + (total_blocks / 32 * sizeof(u32)) + block_num * BLOCK_SIZE;
    memcpy(buffer, block_data, BLOCK_SIZE);
    return true;
}

bool FileSystem::write_block(u32 block_num, const void* buffer) {
    if (block_num >= total_blocks) return false;

    u8* block_data = disk_buffer + total_inodes * sizeof(Inode) + (total_blocks / 32 * sizeof(u32)) + block_num * BLOCK_SIZE;
    memcpy(block_data, buffer, BLOCK_SIZE);
    return true;
}