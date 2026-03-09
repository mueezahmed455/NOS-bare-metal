# NeuralOS Makefile

# Tools
CC = g++
AS = nasm
LD = ld

# Directories
SRC_DIR = .
BUILD_DIR = build
ISO_DIR = $(BUILD_DIR)/isodir

# Target
TARGET = $(BUILD_DIR)/kernel.bin
ISO_TARGET = $(BUILD_DIR)/neuralos.iso

# Compiler flags
CFLAGS = -ffreestanding -fno-stack-protector -fno-exceptions -fno-rtti \
         -m64 -mno-red-zone -mno-sse -mno-sse2 \
         -Wall -Wextra -Werror -O2 -g \
         -I$(SRC_DIR)

# Linker flags
LDFLAGS = -n -static -Bsymbolic -nostdlib

# Source files
ASM_SOURCES = boot.asm interrupts.asm
CPP_SOURCES = kernel.cpp arch.cpp console.cpp memory.cpp

# Object files
ASM_OBJECTS = $(patsubst %.asm,$(BUILD_DIR)/%.o,$(ASM_SOURCES))
CPP_OBJECTS = $(patsubst %.cpp,$(BUILD_DIR)/%.o,$(CPP_SOURCES))
OBJECTS = $(ASM_OBJECTS) $(CPP_OBJECTS)

# Linker script
LINKER_SCRIPT = linker.ld

.PHONY: all clean run debug iso

all: $(TARGET)

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.asm | $(BUILD_DIR)
	$(AS) -f elf64 -o $@ $<

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.cpp | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c -o $@ $<

$(TARGET): $(OBJECTS) $(LINKER_SCRIPT)
	$(LD) $(LDFLAGS) -T $(LINKER_SCRIPT) -o $@ $(OBJECTS)

iso: $(TARGET)
	mkdir -p $(ISO_DIR)/boot/grub
	cp $(TARGET) $(ISO_DIR)/boot/kernel.bin
	echo 'set timeout=0' > $(ISO_DIR)/boot/grub/grub.cfg
	echo 'set default=0' >> $(ISO_DIR)/boot/grub/grub.cfg
	echo '' >> $(ISO_DIR)/boot/grub/grub.cfg
	echo 'menuentry "NeuralOS" {' >> $(ISO_DIR)/boot/grub/grub.cfg
	echo '  multiboot2 /boot/kernel.bin' >> $(ISO_DIR)/boot/grub/grub.cfg
	echo '  boot' >> $(ISO_DIR)/boot/grub/grub.cfg
	echo '}' >> $(ISO_DIR)/boot/grub/grub.cfg
	grub-mkrescue -o $(ISO_TARGET) $(ISO_DIR) 2>/dev/null || echo "Note: grub-mkrescue not available, ISO not created"

run: $(TARGET)
	qemu-system-x86_64 -kernel $(TARGET) -m 512M -no-reboot -no-shutdown

debug: $(TARGET)
	qemu-system-x86_64 -kernel $(TARGET) -m 512M -s -S

iso-run: iso
	qemu-system-x86_64 -cdrom $(ISO_TARGET) -m 512M -no-reboot -no-shutdown

clean:
	rm -rf $(BUILD_DIR)
